import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from waha_service import send_waha_message
from database import SessionLocal
from models import CustomAlarm
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

target_phone = "917259510983@c.us"
message_text = "HI"
person_name = "Kusum"

final_message = f"🔔 *Reminder for {person_name}*\n\n{message_text}"

print("Sending WhatsApp message...")
print(f"Target: {target_phone}")
print(f"Exact Content:\n{final_message}")

success = send_waha_message(target_phone, final_message)

print(f"\nDelivery Result: {'SUCCESS ✅' if success else 'FAILED ❌'}")

# Record in database
db = SessionLocal()
try:
    alarm = CustomAlarm(
        target_type="employee",
        whatsapp_target_id=target_phone,
        report_type="Custom API Reminder",
        frequency="once",
        repeat_interval="none",
        task_notes=final_message,
        trigger_time=now_ist,
        status="sent" if success else "pending"
    )
    db.add(alarm)
    db.commit()
    print(f"Recorded Alarm ID {alarm.id} in Database!")
except Exception as e:
    print("Database record error:", e)
finally:
    db.close()
