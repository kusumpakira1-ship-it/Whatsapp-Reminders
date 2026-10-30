import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from models import ReminderLog

db = get_db_session()
print("Session bind engine:", db.bind.name)

logs = db.query(ReminderLog).filter(ReminderLog.reminder_id == 979).order_by(ReminderLog.id.desc()).limit(10).all()
print(f"Total logs for reminder 979: {len(logs)}")
for l in logs:
    det = (l.details or "").encode('ascii', errors='replace').decode('ascii')
    print(f"[{l.executed_at}] ID: {l.id} | Status: {l.status} | Trigger: {l.trigger_time} | Group: {l.whatsapp_group_id} | Details: {det[:80]}")

# Also check logs around 2026-10-22 23:00
all_logs = db.query(ReminderLog).filter(ReminderLog.trigger_time >= '2026-10-22 22:00:00', ReminderLog.trigger_time <= '2026-10-22 23:59:59').all()
print(f"\nAll logs around 23:00 on 2026-10-22: {len(all_logs)}")
for l in all_logs:
    det = (l.details or "").encode('ascii', errors='replace').decode('ascii')
    print(f"[{l.executed_at}] Reminder ID: {l.reminder_id} | Status: {l.status} | Trigger: {l.trigger_time} | Group: {l.whatsapp_group_id} | Details: {det[:80]}")

db.close()
