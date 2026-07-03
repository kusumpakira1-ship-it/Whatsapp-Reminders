import os
import json
import logging
import requests
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

from database import engine, Base, SessionLocal
from models import Whitelist, RawMessage, ProcessedData, Group, Employee, SystemSetting, CustomAlarm
from ai_processor import process_text, process_image, process_document
from waha_service import download_waha_media, get_waha_chat_name, send_waha_message, send_waha_file
from scheduler import setup_scheduler, scheduler, schedule_custom_alarm
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables in the remote database (if they don't exist)
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the 11 PM scheduler
    setup_scheduler()
    yield
    # Shutdown logic if needed

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="WAHA Farm Automation API", lifespan=lifespan)
os.makedirs("/app/media/reports", exist_ok=True)
app.mount("/media", StaticFiles(directory="/app/media"), name="media")

os.makedirs("/app/static", exist_ok=True)
app.mount("/ui", StaticFiles(directory="/app/static", html=True), name="ui")

@app.get("/messages.json")
async def get_messages_json():
    if os.path.exists("messages.json"):
        return FileResponse("messages.json")
    return {"status": "No messages.json found"}

@app.post("/webhook")
async def waha_webhook(request: Request):
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
    
    is_group = '@g.us' in sender
    group_id = sender if is_group else None
    
    sender_phone = msg.get("participant", sender) if is_group else sender
    for domain in ('@c.us', '@s.whatsapp.net', '@lid'):
        sender_phone = sender_phone.replace(domain, '')
    if group_id:
        group_id = group_id.replace('@g.us', '')

    sender_name = msg.get("pushName") or msg.get("_data", {}).get("pushName") or msg.get("_data", {}).get("notifyName") or ""
    if sender_name.startswith('~'):
        sender_name = sender_name[1:]
    sender_name = sender_name.strip()
    
    if is_group:
        # Try to extract group name if available in typical WAHA payload locations
        group_name_str = msg.get("groupName") or msg.get("_data", {}).get("groupName") or msg.get("chat", {}).get("name")
        if not group_name_str:
            # Fallback to API call
            group_name_str = get_waha_chat_name(sender)
            if group_name_str == sender:
                group_name_str = group_id # Use ID if still fails
        
        display_sender = f"[{group_name_str}] {sender_name} ({sender_phone})" if sender_name else f"[{group_name_str}] {sender_phone}"
    else:
        group_name_str = None
        display_sender = f"{sender_name} ({sender_phone})" if sender_name else sender_phone

    # 1. Extract Data
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
        
    text = msg.get("body") or ""
    timestamp_val = msg.get("timestamp", 0)
    msg_time = datetime.fromtimestamp(timestamp_val, tz=IST).replace(tzinfo=None) if timestamp_val else datetime.now(IST).replace(tzinfo=None)

    # 2. Save Raw Data (First, save all messages!)
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
        db.commit()
        db.refresh(raw_msg)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save raw message: {e}")
        db.close()
        return {"status": "error saving raw"}

    # 3. Apply Filter/Ignore Rules AFTER raw save
    # Ignore messages sent by the bot itself
    if msg.get("fromMe", False):
        logger.info(f"Ignoring message sent by bot itself from processing: {message_id}")
        db.close()
        return {"status": "ignored fromMe"}
        
    # Ignore Status Updates and Channels
    if sender == "status@broadcast" or sender.endswith("@newsletter"):
        logger.info(f"Ignoring status/channel message from processing: {sender}")
        db.close()
        return {"status": "ignored status/channel"}

    # 4. Handle Commands
    if text.startswith('!'):
        command = text.lower().strip()
        
        if command.startswith('!report'):
            parts = command.split()
            range_type = 'daily'
            if len(parts) > 1 and parts[1] in ['weekly', 'monthly', 'yearly']:
                range_type = parts[1]
                
            from report_generator import generate_custom_report
            pdf_path, excel_path, summary_text = generate_custom_report(range_type)
            
            if summary_text:
                send_waha_message(sender, summary_text)
            if pdf_path:
                send_waha_file(sender, pdf_path, caption=f"PDF Report - {pdf_path.split('/')[-1]}")
            if excel_path:
                send_waha_file(sender, excel_path, caption=f"Excel Report - {excel_path.split('/')[-1]}")
                
            db.close()
            return {"status": f"report {range_type} manually requested"}
        elif command == '!manager add':
            from models import ReportRecipient
            recipient_db = SessionLocal()
            try:
                # If command is sent in a group, register the group itself. Otherwise, register the individual.
                recipient_id = msg.get("from") # exact JID (e.g. 1203...@g.us or 9179...@c.us)
                existing = recipient_db.query(ReportRecipient).filter(ReportRecipient.phone_number == recipient_id).first()
                if not existing:
                    recipient_db.add(ReportRecipient(phone_number=recipient_id, is_active=True))
                    recipient_db.commit()
                    send_waha_message(recipient_id, "✅ This chat has been registered to receive automated P&L reports and data entry reminders.")
                else:
                    send_waha_message(recipient_id, "⚠️ This chat is already registered.")
            finally:
                recipient_db.close()
            db.close()
            return {"status": "command handled"}

    # 4. AI Processing Pipeline
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
            
            media_path_lower = media_path.lower()
            if media_path_lower.endswith(('.jpg', '.jpeg', '.png')):
                ai_result = process_image(media_path, caption=text)
                source_type = "image"
            elif media_path_lower.endswith('.pdf'):
                ai_result = process_document(media_path, caption=text)
                source_type = "document"
            else:
                # Unsupported media type
                logger.info(f"Unsupported media type for AI: {media_path}")
    
    # We can close the raw_messages db session now since it's idle during AI
    db.close()
    
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

    # If no media, or media processing failed/returned unknown category, fallback to text processing if caption is available
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
            
            # Only use text result if it succeeded in finding a known category
            if text_cat != "unknown":
                ai_result = text_ai_result
                source_type = "text"

    # 5. Save Processed Data
    if ai_result:
        # Resolve to a list of record dictionaries
        records = []
        if isinstance(ai_result, list):
            records = ai_result
        elif isinstance(ai_result, dict):
            if "records" in ai_result and isinstance(ai_result["records"], list):
                records = ai_result["records"]
            else:
                records = [ai_result]
                
        valid_records_saved = 0
        fresh_db = SessionLocal()
        try:
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
                    fresh_db.add(proc_data)
                    valid_records_saved += 1
            if valid_records_saved > 0:
                fresh_db.commit()
                logger.info(f"Successfully processed message {message_id}: saved {valid_records_saved} records.")
            else:
                logger.info(f"Ignored non-farm message or no valid records found. Text: {text}")
        except Exception as e:
            fresh_db.rollback()
            logger.error(f"Failed to save processed data (fresh session): {e}")
        finally:
            fresh_db.close()

    # 6. Save to local JSON file
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
    except Exception as e:
        logger.error(f"Failed to save to json: {e}")

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
    group_id: int
    report_responsibility: str

class ReminderTimeUpdate(BaseModel):
    time: str

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
    target_id: int
    task_notes: str
    trigger_time: datetime

@app.post("/api/alarms")
def create_alarm(alarm: AlarmCreate):
    db = SessionLocal()
    try:
        new_alarm = CustomAlarm(
            target_type=alarm.target_type,
            target_id=alarm.target_id,
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
                grp = db.query(Group).filter(Group.id == a.target_id).first()
                if grp: target_name = grp.name
                
            result.append({
                "id": a.id,
                "target_type": a.target_type,
                "target_name": target_name,
                "task_notes": a.task_notes,
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
    # Try to unschedule the job if it exists since we're manually triggering it now
    try:
        scheduler.remove_job(f"custom_alarm_{alarm_id}")
    except Exception:
        pass
    
    # Execute immediately
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
