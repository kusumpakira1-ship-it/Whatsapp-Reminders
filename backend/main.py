import os
import json
import logging
import requests
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

from database import engine, Base, SessionLocal
from models import Whitelist, RawMessage, ProcessedData, Group, Employee, SystemSetting, CustomAlarm, WhatsAppMessage, WAHAEvent, Task, EggGodownInventory
from ai_processor import process_text, process_image, process_document
from waha_service import download_waha_media, get_waha_chat_name, send_waha_message, send_waha_file
from scheduler import setup_scheduler, scheduler, schedule_custom_alarm
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables in the remote database (if they don't exist)
Base.metadata.create_all(bind=engine)

def _seed_default_settings():
    """Seed default alert phone/email if not already configured."""
    db = SessionLocal()
    try:
        defaults = {
            "waha_alert_phone": "7259510983",
            "smtp_to": "kusumpakira1@gmail.com"
        }
        for key, value in defaults.items():
            existing = db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if not existing:
                db.add(SystemSetting(key=key, value=value))
        db.commit()
        logger.info("Default WAHA alert settings seeded.")
    except Exception as e:
        logger.error(f"Failed to seed default settings: {e}")
    finally:
        db.close()

_seed_default_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the 11 PM scheduler
    setup_scheduler()
    yield
    # Shutdown logic if needed

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="WAHA Farm Automation API", lifespan=lifespan)

# Allow frontend (nginx on port 80) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("/app/media/reports", exist_ok=True)
app.mount("/media", StaticFiles(directory="/app/media"), name="media")
# Note: /ui static serving removed — frontend is now served by the nginx container

@app.get("/messages.json")
async def get_messages_json():
    if os.path.exists("messages.json"):
        return FileResponse("messages.json")
    return {"status": "No messages.json found"}

def process_message_background(
    message_id: str,
    display_sender: str,
    group_name_str: Optional[str],
    has_media: bool,
    text: str,
    msg_time: datetime,
    payload: dict,
    msg: dict,
    sender_phone: str,
    sender: str,
    is_group: bool,
    sender_name: str
):
    db = SessionLocal()
    try:
        raw_msg = db.query(RawMessage).filter(RawMessage.message_id == message_id).first()
        if not raw_msg:
            logger.error(f"Raw message {message_id} not found in background task.")
            db.close()
            return
            
        ai_result = None
        source_type = "text"
        
        if has_media:
            # Download media
            media_info = msg.get("media") or {}
            media_url_direct = media_info.get("url")
            media_mime = media_info.get("mimetype")
            media_filename = media_info.get("filename")
            media_path = download_waha_media(message_id, media_url=media_url_direct, mimetype=media_mime, filename=media_filename)
            if media_path:
                raw_msg.media_path = media_path
                db.commit()
                
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching raw_msg before AI: {e}")
    finally:
        db.close()
                
    # Proceed with AI Processing WITHOUT holding the database connection open!
    if has_media:
        if media_path:
            media_path_lower = media_path.lower()
            if media_path_lower.endswith(('.jpg', '.jpeg', '.png')):
                ai_result = process_image(media_path, caption=text)
                source_type = "image"
            elif media_path_lower.endswith('.pdf'):
                ai_result = process_document(media_path, caption=text)
                source_type = "document"
            else:
                logger.info(f"Unsupported media type for AI: {media_path}")
        
        # Determine the category from the vision result (if any)
        vision_cat = "unknown"
        if ai_result:
            if isinstance(ai_result, list) and len(ai_result) > 0:
                vision_cat = ai_result[0].get("category", "unknown")
            elif isinstance(ai_result, dict):
                if "records" in ai_result and isinstance(ai_result["records"], list) and len(ai_result["records"]) > 0:
                    vision_cat = ai_result["records"][0].get("category", "unknown")
                else:
                    vision_cat = ai_result.get("category", "unknown")

        # Fallback to text processing
        if (not ai_result or vision_cat == "unknown") and text:
            text_ai_result = process_text(text)
            if text_ai_result:
                text_cat = "unknown"
                if isinstance(text_ai_result, list) and len(text_ai_result) > 0:
                    text_cat = text_ai_result[0].get("category", "unknown")
                elif isinstance(text_ai_result, dict):
                    if "records" in text_ai_result and isinstance(text_ai_result["records"], list) and len(text_ai_result["records"]) > 0:
                        text_cat = text_ai_result["records"][0].get("category", "unknown")
                    else:
                        text_cat = text_ai_result.get("category", "unknown")
                
                if text_cat != "unknown":
                    ai_result = text_ai_result
                    source_type = "text"

    # Re-open database connection to save Processed Data
    db = SessionLocal()
    try:
        if ai_result:
            records = []
            if isinstance(ai_result, list):
                records = ai_result
            elif isinstance(ai_result, dict):
                if "records" in ai_result and isinstance(ai_result["records"], list):
                    records = ai_result["records"]
                else:
                    records = [ai_result]
                    
            valid_records_saved = 0
            allowed_cats = {
                'egg_collection_1', 'egg_collection_2', 'egg_collection', 
                'hen_weight', 'mortality', 'egg_loaded', 'egg_unloaded', 
                'production', 'sales', 'feed', 'raw_material', 'medicine', 
                'expense', 'purchase', 'egg', 'unknown'
            }
            for record in records:
                if isinstance(record, dict):
                    cat = record.get("category") or "unknown"
                    if cat not in allowed_cats:
                        cat = 'unknown'
                    proc_data = ProcessedData(
                        shead_name=record.get("shead_name") or "",
                        category=cat,
                        quantity=record.get("quantity") or 0,
                        unit=record.get("unit") or "",
                        amount=record.get("amount") or 0.0,
                        notes=record.get("notes") or "",
                        sender=display_sender,
                        group_name=group_name_str,
                        source_type=source_type,
                        confidence_score=record.get("confidence_score") or 0.0,
                        processed_time=datetime.now(IST).replace(tzinfo=None),
                        message_id=message_id
                    )
                    db.add(proc_data)
                    valid_records_saved += 1
            if valid_records_saved > 0:
                db.commit()
                logger.info(f"Successfully processed message {message_id}: saved {valid_records_saved} records in background.")
            else:
                logger.info(f"Ignored non-farm message or no valid records found. Text: {text}")
                
        # Save to local JSON file
        try:
            messages = []
            if os.path.exists('messages.json'):
                with open('messages.json', 'r', encoding='utf-8') as f:
                    try:
                        messages = json.load(f)
                    except:
                        pass
                
            messages.append({
                "timestamp": datetime.now(IST).isoformat(),
                "message_id": message_id,
                "sender": display_sender,
                "sender_name": sender_name,
                "is_group": is_group,
                "group_name": group_name_str,
                "raw_text": text,
                "ai_extracted": ai_result
            })
            
            with open('messages.json', 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=4)
        except Exception as json_err:
            logger.error(f"Failed to save to json in background: {json_err}")
            
        # =========================================================================
        # 4. Check for Temperature Alert (>38°C)
        # =========================================================================
        text_lower = text.lower()
        if any(w in text_lower for w in ["temp", "temperature"]):
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', text)
            if match:
                try:
                    temp_val = float(match.group(1))
                    if temp_val > 38.0:
                        alert_msg = (
                            f"🚨 *HIGH TEMPERATURE ALERT* 🚨\n\n"
                            f"The reported temperature is *{temp_val}°C*!\n"
                            f"Please spray water in the sheds immediately to protect the birds. 🚿"
                        )
                        admin_phones = ["917259510983", "919346763549"]
                        # Send alert to admin numbers
                        for admin in admin_phones:
                            logger.info(f"Sending temperature alert to admin: {admin}")
                            send_waha_message(admin, alert_msg)
                        
                        # Also send back to the group/chat where it came from
                        if sender:
                            logger.info(f"Sending temperature alert to chat source: {sender}")
                            send_waha_message(sender, alert_msg)
                except Exception as temp_err:
                    logger.error(f"Error parsing temperature: {temp_err}")

        # =========================================================================
        # 5. Task Workflows Matching Logic
        # =========================================================================
        # Find all pending/approval tasks
        tasks = db.query(Task).filter(Task.status.in_(['pending', 'pending_approval', 'overdue'])).all()
        for t in tasks:
            # Check if this task is assigned to the sender
            clean_sender_phone = "".join(filter(str.isdigit, sender_phone))
            is_assigned = False
            
            # Check assignee phone match
            if t.assigned_person_phone:
                phones = [p.strip() for p in t.assigned_person_phone.split(',') if p.strip()]
                for p in phones:
                    clean_p = "".join(filter(str.isdigit, p))
                    if clean_p in clean_sender_phone or clean_sender_phone in clean_p:
                        is_assigned = True
                        break
            
            # Check group match
            if t.whatsapp_group_id and group_name_str:
                clean_target_group = t.whatsapp_group_id.replace('@g.us', '').strip()
                clean_sender_group = sender.replace('@g.us', '').strip()
                if clean_target_group == clean_sender_group:
                    is_assigned = True
 
            # Fallback for LIDs (Hidden Phone Numbers): Match by Name using fuzzy string matching
            if not is_assigned and t.assigned_person_name and sender_name:
                s_name = sender_name.lower().replace('ss ', '').strip()
                t_name = t.assigned_person_name.lower().replace('ss ', '').strip()
                import difflib
                if len(s_name) >= 3 and len(t_name) >= 3:
                    ratio = difflib.SequenceMatcher(None, s_name, t_name).ratio()
                    if ratio > 0.75 or s_name in t_name or t_name in s_name:
                        is_assigned = True
                        logger.info(f"Assignee matched via fuzzy name fallback: '{sender_name}' matched '{t.assigned_person_name}' (ratio: {ratio:.2f})")

            # If not assigned, skip
            if not is_assigned:
                continue
 
            # Check Rule 1: Approval confirmation logic
            if t.status == 'pending_approval' and t.approver_phone:
                # Only the approver can approve this task!
                clean_approver = "".join(filter(str.isdigit, t.approver_phone))
                if clean_approver in clean_sender_phone or clean_sender_phone in clean_approver:
                    if "approve" in text_lower:
                        t.status = 'completed'
                        t.completion_details = f"Approved by manager {sender_name} ({sender_phone}) at {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}"
                        db.commit()
                        logger.info(f"Task ID {t.id} ('{t.task_name}') approved by {sender_phone}.")
                        
                        approver_name = sender_name or "Manager"
                        target_chat = t.whatsapp_group_id if t.whatsapp_group_id else sender
                        if target_chat:
                            if not target_chat.endswith('@g.us') and not target_chat.endswith('@c.us') and not target_chat.endswith('@lid'):
                                if '-' in target_chat or len(target_chat) > 15:
                                    target_chat += '@g.us'
                                else:
                                    target_chat += '@c.us'
                            confirm_msg = f"task \"{t.task_name} updated and approved by {approver_name}\" marked completed"
                            send_waha_message(target_chat, confirm_msg)
                        continue
                continue
 
            # Check Rule 2: Wednesday Meeting points check
            is_meeting = t.task_type and 'meeting' in t.task_type.lower()
            if is_meeting:
                meeting_keywords = ["points", "minutes", "checklist", "topics", "discussed", "conducting", "conducted"]
                if any(kw in text_lower for kw in meeting_keywords) and len(text) > 20:
                    t.status = 'completed'
                    t.completion_details = text
                    db.commit()
                    logger.info(f"Meeting task ID {t.id} completed. Saved points: '{text[:50]}...'")
                    send_waha_message(sender, f"✅ Meeting follow-up *\"{t.task_name}\"* completed! Points covered saved.")
                    continue
                continue
 
            # Check Rule 3: Feed Formula update (Approval Flow initiator)
            is_approval = t.task_type and ('approval' in t.task_type.lower() or 'feed formula' in t.task_name.lower())
            if is_approval:
                keywords = [k.strip().lower() for k in (t.completion_keywords or 'update,updates,formula,done').split(',') if k.strip()]
                update_kws = ["update", "updated", "updates", "eod", "status", "formula"]
                match_kws = keywords + update_kws
                if any(kw in text_lower for kw in match_kws):
                    t.status = 'pending_approval'
                    t.completion_details = f"Submitted by {sender_name} ({sender_phone}): '{text[:100]}'"
                    db.commit()
                    logger.info(f"Feed Formula task ID {t.id} submitted. Pending approval from approver.")
                    
                    # Look up approver name from Employee table
                    approver_name = t.approver_phone or "Approver"
                    if t.approver_phone:
                        clean_approver = "".join(filter(str.isdigit, t.approver_phone))
                        if len(clean_approver) == 10:
                            alt_phone = "91" + clean_approver
                        else:
                            alt_phone = clean_approver
                        
                        emp = db.query(Employee).filter(
                            (Employee.phone_number == clean_approver) |
                            (Employee.phone_number == alt_phone)
                        ).first()
                        if emp:
                            approver_name = emp.name
                    
                    # Reply back to group/sender
                    reply_msg = f"task {t.task_name} updation completed but approval pending by {approver_name}"
                    send_waha_message(sender, reply_msg)
                    
                    if t.approver_phone:
                        target_approver = t.approver_phone.strip()
                        if not target_approver.endswith('@c.us') and not target_approver.endswith('@g.us'):
                            target_approver += '@c.us'
                        prompt_msg = (
                            f"🔔 *Approval Request* 🔔\n\n"
                            f"The Feed Formula has been updated by *{sender_name}*:\n"
                            f"\"{text}\"\n\n"
                            f"Please reply with *\"Approve {t.task_name}\"* in that group to complete."
                        )
                        send_waha_message(target_approver, prompt_msg)
                    continue
                continue
 
            # Check Rule 4: Generic/Silo tasks match keywords
            keywords = [k.strip().lower() for k in (t.completion_keywords or 'done,completed,cleaned,empty,silo').split(',') if k.strip()]
            update_kws = ["update", "updated", "updates", "eod", "status"]
            has_update = any(kw in text_lower for kw in update_kws)
            task_nouns = [w.lower() for w in t.task_name.split() if len(w) > 3]
            match_update_smart = has_update and any(n in text_lower for n in task_nouns)

            if any(kw in text_lower for kw in keywords) or match_update_smart:
                t.status = 'completed'
                t.completion_details = f"Marked done via WhatsApp message: '{text}'"
                db.commit()
                logger.info(f"Task ID {t.id} ('{t.task_name}') completed via keyword match.")
                send_waha_message(sender, f"✅ Task *\"{t.task_name}\"* marked completed!")
                continue
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error in process_message_background: {e}")
    finally:
        db.close()

@app.post("/webhook")
async def waha_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Only process message events
    event = payload.get("event")
    if event not in ("message", "message.any"):
        return {"status": "ignored event"}

    msg = payload.get("payload", {})
    if not msg:
        return {"status": "no payload"}

    message_id = msg.get("id")
    sender = msg.get("from", "")
    text = msg.get("body") or ""
    
    logger.info(f"Incoming message from {sender} (fromMe={msg.get('fromMe')}). Body: '{text}'")
    
    # Early ignore checks before opening database connections
    if msg.get("fromMe", False) and not text.startswith('!'):
        logger.info(f"Ignoring message sent by bot itself from processing: {message_id}")
        return {"status": "ignored fromMe"}
        
    if sender == "status@broadcast" or sender.endswith("@newsletter"):
        logger.info(f"Ignoring status/channel message from processing: {sender}")
        return {"status": "ignored status/channel"}

    is_group = '@g.us' in sender
    group_id = sender if is_group else None

    # Prefer participantAlt (real phone JID) over participant (may be LID)
    raw_participant = msg.get("participant", sender) if is_group else sender
    participant_alt = msg.get("_data", {}).get("key", {}).get("participantAlt", "") or ""
    # Use participantAlt if it looks like a real phone JID (contains @s.whatsapp.net)
    sender_phone = participant_alt if "@s.whatsapp.net" in participant_alt else raw_participant
    for domain in ('@c.us', '@s.whatsapp.net', '@lid'):
        sender_phone = sender_phone.replace(domain, '')
    if group_id:
        group_id = group_id.replace('@g.us', '')

    sender_name = msg.get("pushName") or msg.get("_data", {}).get("pushName") or msg.get("_data", {}).get("notifyName") or ""
    if sender_name.startswith('~'):
        sender_name = sender_name[1:]
    sender_name = sender_name.strip()
    
    if is_group:
        group_name_str = msg.get("groupName") or msg.get("_data", {}).get("groupName") or msg.get("chat", {}).get("name")
        if not group_name_str:
            group_name_str = get_waha_chat_name(sender)
            if group_name_str == sender:
                group_name_str = group_id
        
        display_sender = f"[{group_name_str}] {sender_name} ({sender_phone})" if sender_name else f"[{group_name_str}] {sender_phone}"
    else:
        group_name_str = None
        display_sender = f"{sender_name} ({sender_phone})" if sender_name else sender_phone

    has_media = msg.get("hasMedia", False)
    media_info = msg.get("media") or {}
    mime_type = media_info.get("mimetype", "")
    
    if has_media:
        if "pdf" in mime_type:
            message_type = "pdf"
        elif "image" in mime_type or "jpeg" in mime_type or "png" in mime_type:
            message_type = "image"
        elif "video" in mime_type:
            message_type = "video"
        else:
            message_type = "document"
    else:
        message_type = "text"
        
    timestamp_val = msg.get("timestamp", 0)
    msg_time = datetime.fromtimestamp(timestamp_val, tz=IST).replace(tzinfo=None) if timestamp_val else datetime.now(IST).replace(tzinfo=None)

    # 1. Save Raw Data synchronously (takes < 5ms)
    db = SessionLocal()
    try:
        existing_msg = db.query(RawMessage).filter(RawMessage.message_id == message_id).first()
        if existing_msg:
            logger.info(f"Message {message_id} already exists. Skipping duplicate event.")
            db.close()
            return {"status": "duplicate message"}

        raw_msg = RawMessage(
            message_id=message_id,
            sender=display_sender,
            group_name=group_name_str,
            timestamp=msg_time,
            message_type=message_type,
            raw_text=text,
            full_webhook_json=json.dumps(payload)
        )
        db.add(raw_msg)

        whatsapp_msg = WhatsAppMessage(
            message_id=message_id,
            group_id=sender if is_group else "",
            sender_id=sender_phone,
            message_text=text or "",
            timestamp=msg_time
        )
        db.add(whatsapp_msg)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save raw message: {e}")
        db.close()
        return {"status": "error saving raw"}
    finally:
        db.close()

    def handle_report_command(range_type_arg: str, sender_arg: str):
        try:
            from report_generator import generate_custom_report
            pdf_path, summary_text = generate_custom_report(range_type_arg)
            if summary_text:
                send_waha_message(sender_arg, summary_text)
            if pdf_path:
                send_waha_file(sender_arg, pdf_path, caption=f"PDF Report - {pdf_path.split('/')[-1]}")
        except Exception as e:
            logger.error(f"Error handling report command: {e}")

    if text.startswith('!'):
        command = text.lower().strip()
        if command.startswith('!report'):
            parts = command.split()
            range_type = 'daily'
            if len(parts) > 1:
                range_type = parts[1]
                
            background_tasks.add_task(handle_report_command, range_type, sender)
            return {"status": f"report {range_type} manually requested (background)"}
            
        elif command == '!manager add':
            from models import ReportRecipient
            recipient_db = SessionLocal()
            try:
                recipient_id = msg.get("from")
                existing = recipient_db.query(ReportRecipient).filter(ReportRecipient.phone_number == recipient_id).first()
                if not existing:
                    recipient_db.add(ReportRecipient(phone_number=recipient_id, is_active=True))
                    recipient_db.commit()
                    send_waha_message(recipient_id, "✅ This chat has been registered to receive automated P&L reports and data entry reminders.")
                else:
                    send_waha_message(recipient_id, "⚠️ This chat is already registered.")
            finally:
                recipient_db.close()
            return {"status": "command handled"}

    # 3. Offload heavy processing to background task (returns 200 OK instantly to WAHA)
    background_tasks.add_task(
        process_message_background,
        message_id,
        display_sender,
        group_name_str,
        has_media,
        text,
        msg_time,
        payload,
        msg,
        sender_phone,
        sender,
        is_group,
        sender_name
    )

    return {"status": "success"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --- UI API Routes for Groups and Employees ---

class GroupCreate(BaseModel):
    name: str
    whatsapp_group_id: str

class EmployeeCreate(BaseModel):
    name: str
    phone_number: str
    group_id: Optional[int] = None
    whatsapp_group_id: Optional[str] = None
    report_responsibility: Optional[str] = None

class ReminderTimeUpdate(BaseModel):
    time: str

class ReportTypesUpdate(BaseModel):
    report_types: List[str]

class TaskTypesUpdate(BaseModel):
    task_types: List[str]

class TaskCreate(BaseModel):
    task_name: str
    task_type: Optional[str] = 'general'
    assigned_person_name: Optional[str] = None
    assigned_person_phone: Optional[str] = None
    whatsapp_group_id: Optional[str] = None
    due_time: str
    completion_keywords: Optional[str] = None
    approver_phone: Optional[str] = None
    frequency: Optional[str] = 'once'
    repeat_interval: Optional[str] = 'none'

class EggGodownInventoryCreate(BaseModel):
    date: str
    opening_balance: int
    closing_balance: int

class CustomMessageSend(BaseModel):
    recipient: str
    message: str



@app.get("/api/settings/report_types")
def get_report_types():
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter_by(key="custom_report_types").first()
        if setting:
            try:
                return json.loads(setting.value)
            except Exception:
                pass
        # Default report list
        default_list = ["Production", "Feed", "Expenses", "Sales", "Profit and Loss"]
        return default_list
    finally:
        db.close()

@app.post("/api/settings/report_types")
def update_report_types(payload: ReportTypesUpdate):
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter_by(key="custom_report_types").first()
        value_str = json.dumps(payload.report_types)
        if not setting:
            setting = SystemSetting(key="custom_report_types", value=value_str)
            db.add(setting)
        else:
            setting.value = value_str
        db.commit()
        return {"status": "success", "report_types": payload.report_types}
    finally:
        db.close()

@app.get("/api/settings/task_types")
def get_task_types():
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter_by(key="custom_task_types").first()
        if setting:
            try:
                return json.loads(setting.value)
            except Exception:
                pass
        default_list = ["Silo Cleaning / Check", "Wednesday Meeting Checklist", "Feed Formula (Requires Approval)"]
        return default_list
    finally:
        db.close()

@app.post("/api/settings/task_types")
def update_task_types(payload: TaskTypesUpdate):
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter_by(key="custom_task_types").first()
        value_str = json.dumps(payload.task_types)
        if not setting:
            setting = SystemSetting(key="custom_task_types", value=value_str)
            db.add(setting)
        else:
            setting.value = value_str
        db.commit()
        return {"status": "success", "task_types": payload.task_types}
    finally:
        db.close()

@app.get("/api/settings/reminders")
def get_reminder_settings():
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter_by(key="targeted_reminder_time").first()
        return {"time": setting.value if setting else "18:10"}
    finally:
        db.close()

@app.post("/api/settings/reminders")
def update_reminder_settings(settings: ReminderTimeUpdate):
    db = SessionLocal()
    try:
        setting = db.query(SystemSetting).filter_by(key="targeted_reminder_time").first()
        if not setting:
            setting = SystemSetting(key="targeted_reminder_time", value=settings.time)
            db.add(setting)
        else:
            setting.value = settings.time
        db.commit()
        
        # Reschedule job in APScheduler
        try:
            hour, minute = map(int, settings.time.split(":"))
            from apscheduler.triggers.cron import CronTrigger
            scheduler.reschedule_job('targeted_reminder_job', trigger=CronTrigger(hour=hour, minute=minute, timezone="Asia/Kolkata"))
        except Exception as e:
            logger.error(f"Failed to reschedule job: {e}")
            
        return {"status": "success", "time": settings.time}
    finally:
        db.close()

class AlarmCreate(BaseModel):
    target_type: str
    target_id: Optional[int] = None
    whatsapp_target_id: Optional[str] = None
    report_type: Optional[str] = None
    frequency: Optional[str] = 'once'
    repeat_interval: Optional[str] = 'none'
    task_notes: str
    trigger_time: datetime

@app.post("/api/alarms")
def create_alarm(alarm: AlarmCreate):
    db = SessionLocal()
    try:
        new_alarm = CustomAlarm(
            target_type=alarm.target_type,
            target_id=alarm.target_id,
            whatsapp_target_id=alarm.whatsapp_target_id,
            report_type=alarm.report_type,
            frequency=alarm.frequency,
            repeat_interval=alarm.repeat_interval,
            task_notes=alarm.task_notes,
            trigger_time=alarm.trigger_time,
            status='pending'
        )
        db.add(new_alarm)
        db.commit()
        db.refresh(new_alarm)
        
        schedule_custom_alarm(new_alarm.id, new_alarm.trigger_time)
        return {"status": "success", "alarm_id": new_alarm.id}
    finally:
        db.close()

@app.get("/api/alarms")
def get_alarms():
    db = SessionLocal()
    try:
        alarms = db.query(CustomAlarm).order_by(CustomAlarm.created_at.desc()).all()
        result = []
        for a in alarms:
            target_name = "Unknown"
            if a.target_type == 'employee':
                emp = db.query(Employee).filter(Employee.id == a.target_id).first()
                if emp: target_name = emp.name
            elif a.target_type == 'group':
                if a.target_id:
                    grp = db.query(Group).filter(Group.id == a.target_id).first()
                    if grp: target_name = grp.name
                elif a.whatsapp_target_id:
                    target_name = a.whatsapp_target_id
                
            result.append({
                "id": a.id,
                "target_type": a.target_type,
                "target_id": a.target_id,
                "whatsapp_target_id": a.whatsapp_target_id,
                "target_name": target_name,
                "task_notes": a.task_notes,
                "report_type": a.report_type,
                "frequency": a.frequency,
                "repeat_interval": a.repeat_interval,
                "trigger_time": a.trigger_time.isoformat(),
                "status": a.status
            })
        return result
    finally:
        db.close()

@app.delete("/api/alarms/{alarm_id}")
def delete_alarm(alarm_id: int):
    db = SessionLocal()
    try:
        alarm = db.query(CustomAlarm).filter(CustomAlarm.id == alarm_id).first()
        if alarm:
            # Try to unschedule from apscheduler
            try:
                scheduler.remove_job(f"custom_alarm_{alarm_id}")
            except Exception:
                pass
            db.delete(alarm)
            db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.post("/api/alarms/{alarm_id}/trigger")
def trigger_alarm_manually(alarm_id: int):
    try:
        scheduler.remove_job(f"custom_alarm_{alarm_id}")
    except Exception:
        pass
    
    from scheduler import execute_custom_alarm
    execute_custom_alarm(alarm_id)
    return {"status": "success"}

@app.get("/api/waha/groups")
def get_waha_groups():
    url = f"{settings.WAHA_URL}/api/{settings.WAHA_SESSION}/groups"
    headers = {"Accept": "application/json"}
    api_key = os.getenv("WAHA_API_KEY", "123")
    if api_key: headers["X-Api-Key"] = api_key
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            groups = []
            data = response.json()
            if isinstance(data, list):
                for g in data:
                    groups.append({"id": g.get("id"), "name": g.get("subject") or g.get("name")})
            elif isinstance(data, dict):
                for k, v in data.items():
                    groups.append({"id": k, "name": v.get("subject") or v.get("name")})
            return {"status": "success", "groups": groups}
        return {"status": "error", "message": "Failed to fetch groups from WAHA"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/groups")
def get_groups():
    db = SessionLocal()
    try:
        groups = db.query(Group).all()
        return [{"id": g.id, "name": g.name, "whatsapp_group_id": g.whatsapp_group_id} for g in groups]
    finally:
        db.close()

@app.post("/api/groups")
def create_group(group: GroupCreate):
    db = SessionLocal()
    try:
        new_group = Group(name=group.name, whatsapp_group_id=group.whatsapp_group_id)
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        return {"id": new_group.id, "name": new_group.name, "whatsapp_group_id": new_group.whatsapp_group_id}
    finally:
        db.close()

@app.delete("/api/groups/{group_id}")
def delete_group(group_id: int):
    db = SessionLocal()
    try:
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        db.delete(group)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.get("/api/employees")
def get_employees():
    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        return [
            {
                "id": e.id, 
                "name": e.name, 
                "phone_number": e.phone_number, 
                "group_id": e.group_id, 
                "whatsapp_group_id": e.whatsapp_group_id,
                "report_responsibility": e.report_responsibility
            } for e in employees
        ]
    finally:
        db.close()

@app.post("/api/employees")
def create_employee(employee: EmployeeCreate):
    db = SessionLocal()
    try:
        new_emp = Employee(
            name=employee.name,
            phone_number=employee.phone_number,
            group_id=employee.group_id,
            whatsapp_group_id=employee.whatsapp_group_id,
            report_responsibility=employee.report_responsibility
        )
        db.add(new_emp)
        db.commit()
        db.refresh(new_emp)
        return {"status": "success", "id": new_emp.id}
    finally:
        db.close()

@app.delete("/api/employees/{employee_id}")
def delete_employee(employee_id: int):
    db = SessionLocal()
    try:
        emp = db.query(Employee).filter(Employee.id == employee_id).first()
        if not emp:
            raise HTTPException(status_code=404, detail="Employee not found")
        db.delete(emp)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()


@app.get("/api/tasks")
def list_tasks():
    db = SessionLocal()
    try:
        tasks = db.query(Task).order_by(Task.due_time.desc()).all()
        return [
            {
                "id": t.id,
                "task_name": t.task_name,
                "task_type": t.task_type,
                "assigned_person_name": t.assigned_person_name,
                "assigned_person_phone": t.assigned_person_phone,
                "whatsapp_group_id": t.whatsapp_group_id,
                "due_time": t.due_time.isoformat(),
                "completion_keywords": t.completion_keywords,
                "status": t.status,
                "approver_phone": t.approver_phone,
                "completion_details": t.completion_details,
                "frequency": t.frequency,
                "repeat_interval": t.repeat_interval,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in tasks
        ]
    finally:
        db.close()

@app.post("/api/tasks")
def create_task(t: TaskCreate):
    db = SessionLocal()
    try:
        try:
            dt = datetime.fromisoformat(t.due_time.replace('Z', '+00:00'))
            dt = dt.astimezone(IST).replace(tzinfo=None)
        except Exception:
            dt = datetime.strptime(t.due_time, "%Y-%m-%d %H:%M:%S")
            
        new_task = Task(
            task_name=t.task_name,
            task_type=t.task_type,
            assigned_person_name=t.assigned_person_name,
            assigned_person_phone=t.assigned_person_phone,
            whatsapp_group_id=t.whatsapp_group_id,
            due_time=dt,
            completion_keywords=t.completion_keywords,
            approver_phone=t.approver_phone,
            frequency=t.frequency,
            repeat_interval=t.repeat_interval,
            status='pending'
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return {"status": "success", "id": new_task.id}
    finally:
        db.close()

@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, t: TaskCreate):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        try:
            dt = datetime.fromisoformat(t.due_time.replace('Z', '+00:00'))
            dt = dt.astimezone(IST).replace(tzinfo=None)
        except Exception:
            dt = datetime.strptime(t.due_time, "%Y-%m-%d %H:%M:%S")

        task.task_name = t.task_name
        task.task_type = t.task_type
        task.assigned_person_name = t.assigned_person_name
        task.assigned_person_phone = t.assigned_person_phone
        task.whatsapp_group_id = t.whatsapp_group_id
        task.due_time = dt
        task.completion_keywords = t.completion_keywords
        task.approver_phone = t.approver_phone
        task.frequency = t.frequency
        task.repeat_interval = t.repeat_interval
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        db.delete(task)
        db.commit()
        return {"status": "success"}
    finally:
        db.close()

@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: int, payload: dict = None):
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task.status = 'completed'
        if payload and "details" in payload:
            task.completion_details = payload["details"]
        db.commit()
        return {"status": "success"}
    finally:
        db.close()




