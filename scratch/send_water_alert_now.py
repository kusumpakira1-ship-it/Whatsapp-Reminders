import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from waha_service import send_waha_message
from database import SessionLocal
from models import CustomAlarm
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)
now_str = now_ist.strftime('%d-%m-%Y %I:%M:%S %p')

group_jid = "120363409544891824@g.us"

alert_message = f"""⚠️ WATER MONITORING ALERT ⚠️

📍 *Location:* Kadubeesanahalli
📟 *MAC:* 40-91-51-C8-0C-C8
💧 *Water Level:* 25%
⚡ *Power Status:* ⚡ ON
🚨 *Alert Reason:* Water Level below (25%)
🕒 *Time:* {now_str}

📍 *Location:* Spice garden
📟 *MAC:* C4-4F-33-24-7C-59
💧 *Water Level:* 0%
⚡ *Power Status:* 🔴 OFF
🚨 *Alert Reason:* Power Status is OFF 🔴 (OFF > 4 hours)
🕒 *Time:* {now_str}"""

print(f"Sending Water Monitoring Alert to Group {group_jid}...")
res = send_waha_message(group_jid, alert_message)
print(f"Delivery Result: {'SUCCESS ✅' if res else 'FAILED ❌'}")

# Record in database queue
db = SessionLocal()
try:
    alarm = CustomAlarm(
        target_type="group",
        whatsapp_target_id=group_jid,
        report_type="Water Monitoring Alert",
        frequency="once",
        repeat_interval="none",
        task_notes=alert_message,
        trigger_time=now_ist,
        status="sent" if res else "pending"
    )
    db.add(alarm)
    db.commit()
    print(f"Recorded Alarm ID {alarm.id} in Database!")
except Exception as e:
    print("Database error:", e)
finally:
    db.close()
