import sys, os
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from database import SessionLocal
from models import CustomAlarm
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

db = SessionLocal()
print("Inserting new custom API alarm into MySQL database...")
alarm = CustomAlarm(
    target_type="employee",
    whatsapp_target_id="917259510983@c.us",
    report_type="Custom API Link Test",
    frequency="once",
    repeat_interval="none",
    task_notes="🔔 *API Link Reminder Test*\n\nHello Kusum! Your URL link trigger is now live and working 100%!",
    trigger_time=now_ist,
    status="pending"
)
db.add(alarm)
db.commit()
print(f"Successfully inserted Alarm ID {alarm.id} into Hostinger MySQL! Task-707 will dispatch it within 5 seconds.")
db.close()
