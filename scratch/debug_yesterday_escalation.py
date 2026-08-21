"""
Debug yesterday (14 Aug 2026) escalation report submissions in backend/scheduler.py.
"""
import sys, os, datetime, pymysql
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

from database import SessionLocal
from models import RawMessage, WhatsAppMessage, ProcessedData, UnifiedReminder, Employee, Group, Task
from sqlalchemy import func

db = SessionLocal()

target_date = datetime.date(2026, 8, 14)
start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
end_of_day = datetime.datetime.combine(target_date, datetime.time.max)

print(f"=== DEBUGGING ESCALATION SUBMISSIONS FOR {target_date} ===")

# Raw messages from both tables
raw_msgs_1 = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day, RawMessage.timestamp <= end_of_day).all()
raw_msgs_2 = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= start_of_day, WhatsAppMessage.timestamp <= end_of_day).all()

print(f"RawMessages count (sunfra_raw_messages): {len(raw_msgs_1)}")
print(f"WhatsAppMessages count (sunfra_whatsapp_messages): {len(raw_msgs_2)}")

print("\n--- SAMPLE SUNFRA_RAW_MESSAGES YESTERDAY ---")
for m in raw_msgs_1[:10]:
    print(f"[{m.timestamp}] Sender: '{m.sender}' | Group: '{m.group_name}' | Text: '{(m.raw_text or '')[:80]}'")

print("\n--- SAMPLE SUNFRA_WHATSAPP_MESSAGES YESTERDAY ---")
for m in raw_msgs_2[:10]:
    print(f"[{m.timestamp}] SenderID: '{m.sender_id}' | GroupID: '{m.group_id}' | Text: '{(m.message_text or '')[:80]}'")

db.close()

