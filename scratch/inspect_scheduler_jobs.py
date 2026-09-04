import re
import sys
from datetime import datetime
import pymysql

sys.stdout.reconfigure(encoding='utf-8')

print("=== 1. ANALYZING SCHEDULER.PY TIME-BASED JOBS & CRONS ===")
with open(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\scheduler.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Find all time matches or cron matches like hour=, minute=, or time comparisons
time_matches = re.findall(r'.*(?:hour|minute|20:|21:|22:|23:|8:00|9:30|11:59|evening|night|pm).*', code, re.IGNORECASE)

print(f"Found {len(time_matches)} lines mentioning times/hours/evening/night/pm:")
seen = set()
for line in time_matches[:50]:
    l = line.strip()
    if l not in seen and not l.startswith('#') and len(l) < 150:
        seen.add(l)
        print("  -", l)

print("\n=== 2. CHECKING TODAY'S (2026-09-01) REMINDERS & TASKS AFTER 8:00 PM (20:00) IN DATABASE ===")
try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 1. Reminders after 20:00 IST today
    cursor.execute("""
        SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status 
        FROM sunfra_unified_reminders 
        WHERE TIME(trigger_time) >= '20:00:00'
        ORDER BY TIME(trigger_time) ASC
    """)
    reminders = cursor.fetchall()
    print(f"\nUnified Reminders scheduled after 8:00 PM (total: {len(reminders)}):")
    for r in reminders:
        print(f"  [ID {r['id']}] Time: {r['trigger_time']} | Name: {r['person_name']} | Group: {r['whatsapp_group_id']} | Reports: {r['report_types']} | Notes: {r['task_notes']} | Freq: {r['frequency']} | Status: {r['status']}")

    # 2. Tasks after 20:00 IST today
    cursor.execute("""
        SELECT id, task_name, assignee_name, assignee_phone, whatsapp_group_id, due_time, frequency, status 
        FROM sunfra_tasks 
        WHERE TIME(due_time) >= '20:00:00'
        ORDER BY TIME(due_time) ASC
    """)
    tasks = cursor.fetchall()
    print(f"\nTasks due after 8:00 PM (total: {len(tasks)}):")
    for t in tasks:
        print(f"  [ID {t['id']}] Due: {t['due_time']} | Task: {t['task_name']} | Assignee: {t['assignee_name']} | Freq: {t['frequency']} | Status: {t['status']}")

    conn.close()
except Exception as e:
    print("MySQL Error:", e)
