"""
Inspect all raw_messages for Aug 17, 2026
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, date, timezone, timedelta
from database import SessionLocal
from models import RawMessage

IST = timezone(timedelta(hours=5, minutes=30))
start_of_day = datetime(2026, 8, 17, 0, 0, 0, tzinfo=IST)
end_of_day = datetime(2026, 8, 17, 23, 59, 59, tzinfo=IST)

db = SessionLocal()
try:
    msgs = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day, RawMessage.timestamp <= end_of_day).all()
    print(f"Total raw messages for Aug 17: {len(msgs)}")
    for m in msgs:
        print(f"[{m.timestamp}] Group: '{m.group_name}' | Sender: '{m.sender}' | Text: '{m.raw_text}'")
        print("-" * 60)
finally:
    db.close()
