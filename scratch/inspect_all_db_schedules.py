import sys, os
from datetime import datetime
import pytz

sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')
from database import get_db_session
from sqlalchemy import text

IST = pytz.timezone('Asia/Kolkata')
now = datetime.now(IST)
print(f"Current Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')} IST ({now.strftime('%A')})")

db = get_db_session()

print("\n--- 1. REPORT RECIPIENTS ---")
recipients = db.execute(text("SELECT * FROM sunfra_report_recipients")).fetchall()
for r in recipients:
    print(" ", dict(r._mapping))

print("\n--- 2. ALL ACTIVE UNIFIED REMINDERS ---")
rems = db.execute(text("SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status FROM sunfra_unified_reminders")).fetchall()
for r in rems:
    print(f"  [ID {r[0]}] {r[1]} ({r[2]}) | Time: {r[6]} | Freq: {r[7]} | Status: {r[8]} | Reports: {r[4]} | Notes: {r[5]}")

print("\n--- 3. SUNFRA_TASKS (SAMPLE COLUMNS & DATA) ---")
tasks_cols = db.execute(text("DESCRIBE sunfra_tasks")).fetchall()
print("Tasks columns:", [c[0] for c in tasks_cols])
tasks = db.execute(text("SELECT * FROM sunfra_tasks LIMIT 10")).fetchall()
for t in tasks:
    print(" ", dict(t._mapping))

print("\n--- 4. SUNFRA_CUSTOM_ALARMS ---")
alarm_cols = db.execute(text("DESCRIBE sunfra_custom_alarms")).fetchall()
print("Alarm columns:", [c[0] for c in alarm_cols])
alarms = db.execute(text("SELECT * FROM sunfra_custom_alarms")).fetchall()
for a in alarms:
    print(" ", dict(a._mapping))

db.close()
