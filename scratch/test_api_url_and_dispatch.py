import sys, os, requests, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from database import SessionLocal
from models import CustomAlarm
from waha_service import send_waha_message
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

print("=== 1. Hitting Live Web API Link ===")
url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?phone=7259510983&name=Kusum&message=Hello+from+API+Link&json=1"
try:
    res = requests.get(url, timeout=10)
    print("API HTTP Status:", res.status_code)
    print("API Response:", res.text[:300])
except Exception as e:
    print("API Error:", e)

print("\n=== 2. Polling Database for Pending API Alarms ===")
db = SessionLocal()
now_ist = datetime.now(IST).replace(tzinfo=None)
pending_alarms = db.query(CustomAlarm).filter(
    CustomAlarm.status == 'pending',
    CustomAlarm.trigger_time <= now_ist
).all()

print(f"Found {len(pending_alarms)} pending alarms ready for dispatch!")
for alarm in pending_alarms:
    target = alarm.whatsapp_target_id
    text = alarm.task_notes
    print(f"Dispatching Alarm ID {alarm.id} to {target}...")
    success = send_waha_message(target, text)
    if success:
        alarm.status = 'sent'
        db.commit()
        print(f"Alarm ID {alarm.id} DISPATCHED & MARKED SENT ✅")
    else:
        print(f"Alarm ID {alarm.id} dispatch failed ❌")

db.close()
