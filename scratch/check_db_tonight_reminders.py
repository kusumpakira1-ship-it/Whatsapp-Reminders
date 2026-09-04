import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("=== CHECKING SQLITE REMINDERS & TASKS AFTER 8:00 PM ===")
conn = sqlite3.connect(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\whatsapp_reminders.sqlite')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, person_name, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status FROM sunfra_unified_reminders WHERE time(trigger_time) >= '20:00:00'")
rems = cursor.fetchall()
print(f"Custom Unified Reminders scheduled after 8:00 PM today (Count: {len(rems)}):")
for r in rems:
    print(f"  - [{r['trigger_time']}] {r['person_name']} | Group: {r['whatsapp_group_id']} | Notes: {r['task_notes']} | Status: {r['status']}")

cursor.execute("SELECT id, task_name, assigned_person_name, whatsapp_group_id, due_time, frequency, status FROM sunfra_tasks WHERE time(due_time) >= '20:00:00'")
tasks = cursor.fetchall()
print(f"\nTasks due after 8:00 PM today (Count: {len(tasks)}):")
for t in tasks:
    print(f"  - [{t['due_time']}] {t['task_name']} | Assignee: {t['assigned_person_name']} | Status: {t['status']}")

conn.close()
