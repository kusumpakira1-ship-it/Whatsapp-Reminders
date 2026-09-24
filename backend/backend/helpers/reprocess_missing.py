import json
import logging
from datetime import datetime, timezone, timedelta
import os
import sys
import time
import re
from sqlalchemy import and_

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import RawMessage, ProcessedData
from ai_processor import process_text, process_image, process_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Reprocessor")

IST = timezone(timedelta(hours=5, minutes=30))

def is_noise_message(text: str) -> bool:
    cleaned = text.lower().strip()
    if not cleaned:
        return True
        
    # Standard short acknowledgments & greetings
    noise_words = {
        'ok', 'out', 'in', 'hello', 'hi', 'good morning', 'good evening', 
        'reached', 'reached now', 'done', 'lunch', 'dinner', 'tea', 'break',
        'yes', 'no', 'thanks', 'thank you', 'welcome', 'test', 'status', 'oye', 'hello everyone'
    }
    if cleaned in noise_words:
        return True
        
    # Check "xxxx in" or "xxxx out" (worker attendance check-ins)
    if cleaned.endswith(' in') or cleaned.endswith(' out') or cleaned.endswith(' in.') or cleaned.endswith(' out.'):
        return True
        
    # Check if text is just a bare shead name without any data (e.g. "Shead1", "Shed 3", "s2")
    if re.match(r'^(shead|shed|s)\s*\d+$', cleaned):
        return True
        
    # Check if text is just a name of labourers/contractors check-in
    if "labour" in cleaned or "labor" in cleaned or "loader" in cleaned:
        return True
        
    return False

def reprocess_missing():
    raw_msgs = []
    
    # 1. Fetch missing messages and close session immediately to avoid timeouts
    db = SessionLocal()
    try:
        cutoff = datetime.now() - timedelta(hours=24)
        print("Querying missing raw messages from database...")
        sys.stdout.flush()
        
        from sqlalchemy import or_
        raw_msgs = db.query(RawMessage).outerjoin(
            ProcessedData, RawMessage.message_id == ProcessedData.message_id
        ).filter(
            and_(
                RawMessage.timestamp >= cutoff,
                or_(
                    ProcessedData.id == None,
                    ProcessedData.notes == "AI processing failed or unreachable",
                    ProcessedData.category == "unknown"
                )
            )
        ).order_by(RawMessage.timestamp.asc()).all()
        
        print(f"Total missing raw messages in last 24 hours: {len(raw_msgs)}")
        sys.stdout.flush()
    except Exception as e:
        logger.error(f"Failed to query raw messages: {e}")
        return
    finally:
        db.close()
        
    # Load messages.json if exists
    messages_json_path = 'messages.json'
    messages_json_data = []
    if os.path.exists(messages_json_path):
        try:
            with open(messages_json_path, 'r', encoding='utf-8') as f:
                messages_json_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load messages.json: {e}")

    json_msg_map = {m.get('message_id'): m for m in messages_json_data if m.get('message_id')}

    reprocessed_count = 0
    records_saved = 0
    skipped_noise_count = 0

    for r_msg in raw_msgs:
        msg_id = r_msg.message_id
        text = r_msg.raw_text or ""
        
        # Pre-filter noise to avoid wasting API quota and execution time
        if is_noise_message(text):
            skipped_noise_count += 1
            if msg_id in json_msg_map:
                json_msg_map[msg_id]["ai_extracted"] = {
                    "shead_name": "",
                    "category": "unknown",
                    "quantity": 0,
                    "unit": "",
                    "amount": 0.0,
                    "notes": "Filtered as noise check-in / greeting",
                    "confidence_score": 0.0,
                    "processed_text": text
                }
                json_msg_map[msg_id]["reprocessed"] = True
            continue
            
        # Verify it wasn't processed since we started (using a fresh short session)
        verify_db = SessionLocal()
        try:
            existing_proc = verify_db.query(ProcessedData).filter(ProcessedData.message_id == msg_id).first()
            if existing_proc:
                continue
        finally:
            verify_db.close()
            
        print("="*60)
        print(f"REPROCESSING MISSING MESSAGE:")
        print(f"ID: {r_msg.id} | MsgID: {msg_id}")
        print(f"Sender: {r_msg.sender} | Time: {r_msg.timestamp}")
        print(f"Type: {r_msg.message_type} | Text: {repr(text)}")
        sys.stdout.flush()
        
        ai_result = None
        source_type = r_msg.message_type
        
        # Retry mechanism for rate limits
        retries = 3
        while retries > 0:
            try:
                if r_msg.media_path:
                    media_path_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), r_msg.media_path.lstrip('/'))
                    if not os.path.exists(media_path_abs):
                        media_path_abs = r_msg.media_path
                    
                    print(f"Processing media: {media_path_abs}")
                    sys.stdout.flush()
                    if os.path.exists(media_path_abs):
                        if media_path_abs.lower().endswith(('.jpg', '.jpeg', '.png')):
                            ai_result = process_image(media_path_abs, caption=text)
                            source_type = "image"
                        elif media_path_abs.lower().endswith('.pdf'):
                            ai_result = process_document(media_path_abs, caption=text)
                            source_type = "document"
                        else:
                            print(f"Unsupported media extension: {media_path_abs}")
                            sys.stdout.flush()
                    else:
                        print(f"Media file not found: {media_path_abs}")
                        sys.stdout.flush()
                
                if not ai_result and text:
                    ai_result = process_text(text)
                    source_type = "text"
                
                # Check if result indicates API failure/rate limit
                if ai_result and ai_result.get("notes") == "AI processing failed or unreachable":
                    raise ValueError("Groq Rate Limit/Failure detected from dummy fallback")
                    
                break # Success
                
            except Exception as e:
                print(f"Rate limit or API failure hit: {e}. Sleeping 40 seconds before retry...")
                sys.stdout.flush()
                time.sleep(40)
                retries -= 1
                ai_result = None

        # Sleep 1 second between loop iterations (Ollama)
        print("Sleeping 1s...")
        sys.stdout.flush()
        time.sleep(1)

        if ai_result:
            print(f"AI Result: {json.dumps(ai_result, indent=2)}")
            sys.stdout.flush()
            
            # Resolve to list of record dicts
            records = []
            if isinstance(ai_result, list):
                records = ai_result
            elif isinstance(ai_result, dict):
                if "records" in ai_result and isinstance(ai_result["records"], list):
                    records = ai_result["records"]
                else:
                    records = [ai_result]
            
            valid_records_saved = 0
            
            # Open a fresh connection ONLY when we need to write, and close it immediately
            write_db = SessionLocal()
            try:
                # Delete any existing processed data for this message to prevent duplicates/placeholders
                write_db.query(ProcessedData).filter(ProcessedData.message_id == msg_id).delete()
                
                for record in records:
                    if isinstance(record, dict) and record.get("category", "unknown") != "unknown":
                        proc_data = ProcessedData(
                            shead_name=record.get("shead_name") or "",
                            category=record.get("category") or "unknown",
                            quantity=record.get("quantity") or 0,
                            unit=record.get("unit") or "",
                            amount=record.get("amount") or 0.0,
                            notes=record.get("notes") or "",
                            sender=r_msg.sender,
                            group_name=r_msg.group_name,
                            source_type=source_type,
                            confidence_score=record.get("confidence_score") or 0.0,
                            processed_time=datetime.now(IST).replace(tzinfo=None),
                            message_id=msg_id
                        )
                        write_db.add(proc_data)
                        valid_records_saved += 1
                        records_saved += 1
                
                if valid_records_saved > 0:
                    write_db.commit()
                    reprocessed_count += 1
                    print(f"--> Saved {valid_records_saved} records to database successfully!")
                    sys.stdout.flush()
                else:
                    print("--> Classified as unknown or non-farm record. Skipping DB save.")
                    sys.stdout.flush()
            except Exception as e:
                write_db.rollback()
                logger.error(f"Failed to commit reprocessed records for msg_id {msg_id}: {e}")
            finally:
                write_db.close()

            # Update messages.json map
            if msg_id in json_msg_map:
                json_msg_map[msg_id]["ai_extracted"] = ai_result
                json_msg_map[msg_id]["reprocessed"] = True
            else:
                messages_json_data.append({
                    "timestamp": datetime.now(IST).isoformat(),
                    "message_id": msg_id,
                    "sender": r_msg.sender,
                    "is_group": '@g.us' in r_msg.sender or (r_msg.group_name is not None),
                    "group_name": r_msg.group_name,
                    "raw_text": text,
                    "ai_extracted": ai_result,
                    "reprocessed": True
                })
        else:
            print("--> AI extraction returned null or failed.")
            sys.stdout.flush()

    # Save updated messages.json
    if messages_json_data:
        try:
            with open(messages_json_path, 'w', encoding='utf-8') as f:
                json.dump(messages_json_data, f, indent=4)
            print(f"Successfully updated messages.json with reprocessed entries.")
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Failed to save updated messages.json: {e}")

    print("="*60)
    print(f"Reprocessing completed! Skipped {skipped_noise_count} noise entries. Reprocessed {reprocessed_count} farm messages, saved {records_saved} records in database.")
    sys.stdout.flush()

if __name__ == "__main__":
    reprocess_missing()
