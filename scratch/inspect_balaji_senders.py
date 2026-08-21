"""
Inspect exact raw_sender values for Balaji Team messages.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage

db = SessionLocal()
start_of_day = datetime.datetime(2026, 8, 13, 0, 0, 0)
msgs = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day, RawMessage.group_name.like('%Balaji%')).all()

for m in msgs:
    print(f"Sender: '{m.sender}' | Group: '{m.group_name}' | Text: '{m.raw_text}'")

db.close()

