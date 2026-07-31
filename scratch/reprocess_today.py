import os, sys, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from models import RawMessage, ProcessedData
from ai_processor import parse_farm_text

db = SessionLocal()
today = datetime.datetime.now().date()
raw_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= f"{today} 00:00:00").all()
print(f"Reprocessing {len(raw_msgs)} raw messages from today ({today})...")

reprocessed_count = 0
for msg in raw_msgs:
    text = msg.raw_text or ""
    if not text:
        continue
    parsed = parse_farm_text(text)
    if parsed:
        # Delete existing unknown entry for this message_id if any
        db.query(ProcessedData).filter(ProcessedData.message_id == msg.message_id).delete()
        for rec in parsed:
            p = ProcessedData(
                message_id=msg.message_id,
                shead_name=rec['shead_name'],
                category=rec['category'],
                quantity=rec['quantity'],
                unit=rec['unit'],
                notes=rec.get('notes', ''),
                sender=msg.sender,
                group_name=msg.group_name or '',
                source_type='text',
                confidence_score=1.0,
                processed_time=msg.timestamp
            )
            db.add(p)
            reprocessed_count += 1

db.commit()
print(f"Reprocessing complete! Inserted {reprocessed_count} structured records for today.")

# Check category counts in ProcessedData for today
data = db.query(ProcessedData).filter(ProcessedData.processed_time >= f"{today} 00:00:00").all()
cats = {}
for d in data:
    cats[d.category] = cats.get(d.category, 0) + 1
print("Updated Categories Summary Today:", cats)

db.close()
