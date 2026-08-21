"""
Inspect today's actual WhatsApp messages for Accounts Poultry and Sunfra Feeds
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, timezone, timedelta
from database import SessionLocal
from models import RawMessage, WhatsAppMessage, ProcessedData
from sqlalchemy import func, desc

IST = timezone(timedelta(hours=5, minutes=30))
today_date = datetime.now(IST).date()

db = SessionLocal()
try:
    print(f"=== TODAY'S RAW MESSAGES ({today_date}) ===")
    raw_msgs = db.query(RawMessage).filter(func.date(RawMessage.timestamp) == today_date).order_by(desc(RawMessage.timestamp)).all()
    print(f"Total raw messages today: {len(raw_msgs)}")
    for m in raw_msgs:
        print(f"[{m.timestamp}] Group: {m.group_name} | Sender: {m.sender}")
        print(f"Text: {m.raw_text}")
        print("-" * 50)

    print(f"\n=== TODAY'S WHATSAPP MESSAGES ({today_date}) ===")
    wa_msgs = db.query(WhatsAppMessage).filter(func.date(WhatsAppMessage.timestamp) == today_date).order_by(desc(WhatsAppMessage.timestamp)).all()
    print(f"Total WhatsApp messages today: {len(wa_msgs)}")
    for m in wa_msgs:
        print(f"[{m.timestamp}] Group: {m.group_id} | Sender: {m.sender_id}")
        print(f"Text: {m.message_text}")
        print("-" * 50)

    print(f"\n=== TODAY'S PROCESSED DATA ({today_date}) ===")
    proc_msgs = db.query(ProcessedData).filter(func.date(ProcessedData.processed_time) == today_date).all()
    print(f"Total processed data today: {len(proc_msgs)}")
    for p in proc_msgs:
        print(f"Group: {p.group_name} | Cat: {p.category} | Notes: {p.notes}")
        print("-" * 50)
finally:
    db.close()
