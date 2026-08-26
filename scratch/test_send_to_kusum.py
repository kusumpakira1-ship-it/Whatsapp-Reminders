import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from waha_service import send_waha_message
from database import SessionLocal
from models import CustomAlarm, UnifiedReminder
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

target_phone = "917259510983@c.us"
test_msg = "🔔 *API Link Test Message*\n\nHello Kusum! This is a live test from your custom URL reminder link system."

print(f"Sending test WhatsApp message to {target_phone}...")
success = send_waha_message(target_phone, test_msg)
print(f"Result: {'SUCCESS ✅' if success else 'FAILED ❌'}")

# Also record in custom alarms table
db = SessionLocal()
try:
    alarm = CustomAlarm(
        target_type="employee",
        whatsapp_target_id=target_phone,
        report_type="Custom API Reminder Test",
        frequency="once",
        repeat_interval="none",
        task_notes=test_msg,
        trigger_time=now_ist,
        status="sent" if success else "pending"
    )
    db.add(alarm)
    db.commit()
    print(f"Recorded alarm ID {alarm.id} in database!")
except Exception as e:
    print("Database error:", e)
finally:
    db.close()
