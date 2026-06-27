import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager

from db.database import engine, Base, SessionLocal
from db.models import Whitelist, RawMessage, ProcessedData
from services.ai_processor import process_text, process_image, process_document
from services.waha_service import download_waha_media, get_waha_chat_name, send_waha_message, send_waha_file
from services.scheduler import setup_scheduler
from core.config import settings

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
    
    # Ignore Status Updates and Channels
    if sender == "status@broadcast" or sender.endswith("@newsletter"):
        logger.info(f"Ignoring status/channel message from {sender}")
        return {"status": "ignored status/channel"}

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
    message_type = msg.get("type", "unknown")
    text = msg.get("body") or ""
    timestamp_val = msg.get("timestamp", 0)
    msg_time = datetime.fromtimestamp(timestamp_val) if timestamp_val else datetime.now()
    has_media = msg.get("hasMedia", False) or msg.get("type") in ("image", "document")
    
    # 2. Handle Commands
    if text.startswith('!'):
        command = text.lower().strip()
        
        if command.startswith('!report'):
            parts = command.split()
            range_type = 'daily'
            if len(parts) > 1 and parts[1] in ['weekly', 'monthly', 'yearly']:
                range_type = parts[1]
                
            from services.report_generator import generate_custom_report
            pdf_path, excel_path, summary_text = generate_custom_report(range_type)
            
            if summary_text:
                send_waha_message(sender, summary_text)
            if pdf_path:
                send_waha_file(sender, pdf_path, caption=f"PDF Report - {pdf_path.split('/')[-1]}")
            if excel_path:
                send_waha_file(sender, excel_path, caption=f"Excel Report - {excel_path.split('/')[-1]}")
                
            return {"status": f"report {range_type} manually requested"}
        elif command == '!manager add':
            from db.models import ReportRecipient
            db = SessionLocal()
            try:
                # If command is sent in a group, register the group itself. Otherwise, register the individual.
                recipient_id = msg.get("from") # exact JID (e.g. 1203...@g.us or 9179...@c.us)
                existing = db.query(ReportRecipient).filter(ReportRecipient.phone_number == recipient_id).first()
                if not existing:
                    db.add(ReportRecipient(phone_number=recipient_id, is_active=True))
                    db.commit()
                    send_waha_message(recipient_id, "✅ This chat has been registered to receive automated P&L reports and data entry reminders.")
                else:
                    send_waha_message(recipient_id, "⚠️ This chat is already registered.")
            finally:
                db.close()
            return {"status": "command handled"}

    # 3. Save Raw Data
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
            media_url=None, # Update if waha provides URL directly
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
            
            if media_path.endswith(('.jpg', '.jpeg', '.png')):
                ai_result = process_image(media_path, caption=text)
                source_type = "image"
            elif media_path.endswith('.pdf'):
                ai_result = process_document(media_path, caption=text)
                source_type = "document"
            else:
                # Unsupported media type
                logger.info(f"Unsupported media type for AI: {media_path}")
    
    # We can close the raw_messages db session now since it's idle during AI
    db.close()
    
    # If no media or media processing failed/skipped, fallback to text if available
    if not ai_result and text:
        ai_result = process_text(text)

    # 5. Save Processed Data
    if ai_result:
        # Normalize ai_result to a list of records
        records_list = []
        if isinstance(ai_result, dict):
            if "records" in ai_result and isinstance(ai_result["records"], list):
                records_list = ai_result["records"]
            else:
                # Legacy single-record dictionary
                records_list = [ai_result]
        elif isinstance(ai_result, list):
            # If Ollama returned a list directly
            records_list = ai_result
            
        fresh_db = SessionLocal()
        try:
            saved_count = 0
            for record in records_list:
                if not isinstance(record, dict):
                    continue
                if record.get("category", "unknown") == "unknown":
                    logger.info(f"Ignored record with unknown category. Text: {text}")
                    continue
                
                proc_data = ProcessedData(
                    shead_name=record.get("shead_name", ""),
                    category=record.get("category", "unknown"),
                    quantity=record.get("quantity", 0),
                    unit=record.get("unit", ""),
                    amount=record.get("amount", 0.0),
                    notes=record.get("notes", ""),
                    sender=display_sender,
                    group_name=group_name_str,
                    source_type=source_type,
                    confidence_score=record.get("confidence_score", 0.0),
                    processed_time=datetime.now(),
                    message_id=message_id
                )
                fresh_db.add(proc_data)
                saved_count += 1
                
            if saved_count > 0:
                fresh_db.commit()
                logger.info(f"Successfully processed message {message_id}: saved {saved_count} records")
            else:
                logger.info(f"No valid farm records found in message {message_id}")
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
            "timestamp": datetime.now().isoformat(),
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
