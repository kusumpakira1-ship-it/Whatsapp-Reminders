import re
import sys
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

print("=== 1. DETAILED JOBS DEFINED IN SCHEDULER.PY ===")
with open(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\scheduler.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Find all scheduler.add_job or cron schedules or function schedules in scheduler.py
job_defs = re.findall(r'def\s+[a-zA-Z0-9_]+\([^)]*\):[\s\S]*?(?=def|\Z)', code)

evening_jobs = []
for job in job_defs:
    lines = job.split('\n')
    func_name = lines[0].strip()
    # Check if function relates to evening / night / 8pm / 9pm / 10pm / 9:30 / 11:59 or cron
    if any(k in job.lower() for k in ['8:00', '8 pm', '8pm', '9:00', '9 pm', '9pm', '10:00', '10 pm', '10pm', '9:30', '11:59', 'night', 'evening', 'escalation', 'summary', 'audit', 'daily_report']):
        evening_jobs.append((func_name, job))

print(f"Found {len(evening_jobs)} relevant evening/night functions in scheduler.py:\n")
for name, body in evening_jobs:
    print(f"==================================================")
    print(f"FUNCTION: {name}")
    print(f"==================================================")
    # Print docstring or first 25 lines of function
    lines = body.split('\n')
    for l in lines[:30]:
        print("  ", l)
    print("\n")

print("\n=== 2. CHECKING LOCAL SQLITE DATABASE FOR REMINDERS & TASKS AFTER 8:00 PM ===")
try:
    conn = sqlite3.connect(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\whatsapp_reminders.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status FROM sunfra_unified_reminders WHERE time(trigger_time) >= '20:00:00'")
    rems = cursor.fetchall()
    print(f"SQLite Reminders after 8:00 PM (total: {len(rems)}):")
    for r in rems:
        print(f"  [ID {r['id']}] Trigger: {r['trigger_time']} | Name: {r['person_name']} | Group: {r['whatsapp_group_id']} | Reports: {r['report_types']} | Freq: {r['frequency']} | Status: {r['status']}")

    cursor.execute("SELECT id, task_name, assignee_name, whatsapp_group_id, due_time, frequency, status FROM sunfra_tasks WHERE time(due_time) >= '20:00:00'")
    tasks = cursor.fetchall()
    print(f"\nSQLite Tasks after 8:00 PM (total: {len(tasks)}):")
    for t in tasks:
        print(f"  [ID {t['id']}] Due: {t['due_time']} | Task: {t['task_name']} | Assignee: {t['assignee_name']} | Freq: {t['frequency']} | Status: {t['status']}")

    conn.close()
except Exception as e:
    print("SQLite Error:", e)
