import sys, datetime
sys.path.append('/app')
from database import SessionLocal
from models import UnifiedReminder, ReminderLog
from waha_service import send_waha_message

db = SessionLocal()
r = db.query(UnifiedReminder).filter(UnifiedReminder.id == 233).first()
group_jid = r.whatsapp_group_id if r else "120363427856964756@g.us"
if not group_jid.endswith('@g.us'):
    group_jid += '@g.us'

msg = "🔔 *Reminder: Sunfra P&L*\n\nPlease submit today's Daily Work Update / Profit Summary report(s)."
print(f"Sending reminder to Sunfra P&L group ({group_jid})...")
send_waha_message(group_jid, msg)

log = ReminderLog(
    reminder_id=233,
    report_types="Daily Work Update",
    person_name="Team",
    whatsapp_group_id=group_jid,
    trigger_time=datetime.datetime.now(),
    status="sent",
    details="Sent directly via urgent request"
)
db.add(log)
if r:
    r.status = 'sent'
db.commit()
print("Sunfra P&L reminder sent and logged successfully!")
