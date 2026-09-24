from database import get_db_session
from sqlalchemy import text

db = get_db_session()

print("=== sunfra_unified_reminders at 17:00 ===")
rows = db.execute(text("SELECT * FROM sunfra_unified_reminders WHERE DATE(trigger_time) = '2026-09-23' AND TIME(trigger_time) = '17:00:00'")).fetchall()
for r in rows:
    print(dict(r._mapping))

print("\n=== sunfra_unified_reminders with Silo or Checklist ===")
rows = db.execute(text("SELECT * FROM sunfra_unified_reminders WHERE report_types LIKE '%Silo%' OR task_notes LIKE '%Silo%' OR report_types LIKE '%Checklist%' OR task_notes LIKE '%Checklist%'")).fetchall()
for r in rows:
    print(dict(r._mapping))

print("\n=== sunfra_reminder_logs for today ===")
try:
    rows = db.execute(text("SELECT * FROM sunfra_reminder_logs WHERE DATE(sent_at) = '2026-09-23'")).fetchall()
    for r in rows:
        print(dict(r._mapping))
except Exception as e:
    print(f"Error logs: {e}")

db.close()
