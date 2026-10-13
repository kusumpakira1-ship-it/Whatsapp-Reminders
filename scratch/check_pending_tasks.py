import sys, os
from datetime import datetime
import pytz

sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')
from database import get_db_session
from sqlalchemy import text

db = get_db_session()
print("=== PENDING / ACTIVE SUNFRA_TASKS ===")
tasks = db.execute(text("SELECT id, task_name, assigned_person_name, due_time, frequency, status FROM sunfra_tasks WHERE status != 'completed'")).fetchall()
print(f"Count: {len(tasks)}")
for t in tasks:
    print(f"  [Task ID {t[0]}] {t[1]} | Assignee: {t[2]} | Due: {t[3]} | Freq: {t[4]} | Status: {t[5]}")

print("\n=== SYSTEM SETTINGS TARGETED REMINDER TIME ===")
target_time = db.execute(text("SELECT `value` FROM sunfra_system_settings WHERE `key` = 'targeted_reminder_time'")).scalar()
print("Targeted reminder time setting:", target_time)

db.close()
