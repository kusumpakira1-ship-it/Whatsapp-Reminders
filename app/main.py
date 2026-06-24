import os
import json
import logging
from datetime import datetime
from fastapi import FastAPI, Request, Depends, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from db.database import engine, Base, get_db
from db.models import Whitelist, RawMessage, ProcessedData
from services.ai_processor import process_text, process_image, process_document
from services.waha_service import download_waha_media
from services.scheduler import setup_scheduler

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

app = FastAPI(title="WAHA Farm Automation API", lifespan=lifespan)

@app.post("/webhook")
async def waha_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Only process message events
    event = payload.get("event")
    if event not in ("message", "message.any"):
        return {"status": "ignored event"}

    msg = payload.get("payload", {})
    message_id = msg.get("id")
    sender = msg.get("from", "")
    is_group = '@g.us' in sender
    group_id = sender if is_group else None
    
    sender_phone = msg.get("participant", sender) if is_group else sender
    sender_phone = sender_phone.replace('@c.us', '')
    if group_id:
        group_id = group_id.replace('@g.us', '')

    # 1. Whitelist Check (Disabled as per request - processing ALL numbers/groups)
    is_whitelisted = True 


    # 2. Extract Data
    message_type = msg.get("type", "unknown")
    text = msg.get("body", "")
    timestamp_val = msg.get("timestamp", 0)
    msg_time = datetime.fromtimestamp(timestamp_val) if timestamp_val else datetime.now()
    has_media = msg.get("hasMedia", False)

    # 3. Save Raw Data
    raw_msg = RawMessage(
        message_id=message_id,
        sender=sender_phone,
        group_name=group_id,
        timestamp=msg_time,
        message_type=message_type,
        raw_text=text,
        media_url=None, # Update if waha provides URL directly
        full_webhook_json=payload
    )
    db.add(raw_msg)
    try:
        db.commit()
        db.refresh(raw_msg)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save raw message: {e}")
        return {"status": "error saving raw"}

    # 4. AI Processing Pipeline
    ai_result = None
    source_type = "text"
    
    if has_media:
        # Download media
        media_path = download_waha_media(message_id)
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
    
    # If no media or media processing failed/skipped, fallback to text if available
    if not ai_result and text:
        ai_result = process_text(text)

    # 5. Save Processed Data
    if ai_result:
        proc_data = ProcessedData(
            farm_name=ai_result.get("farm_name", ""),
            category=ai_result.get("category", "unknown"),
            quantity=ai_result.get("quantity", 0),
            unit=ai_result.get("unit", ""),
            notes=ai_result.get("notes", ""),
            sender=sender_phone,
            source_type=source_type,
            confidence_score=ai_result.get("confidence_score", 0.0),
            processed_time=datetime.now(),
            message_id=message_id
        )
        db.add(proc_data)
        db.commit()
        logger.info(f"Successfully processed message {message_id}")

    return {"status": "success"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
