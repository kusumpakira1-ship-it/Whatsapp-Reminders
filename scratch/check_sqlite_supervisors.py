"""
Inspect Supervisors rows in local SQLite backup
"""
import sqlite3

sqlite_file = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\whatsapp_reminders.sqlite"
conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()

print("=== ALL ROWS IN LOCAL SQLITE sunfra_unified_reminders ===")
cursor.execute("SELECT id, person_name, whatsapp_group_id, report_types, task_notes, trigger_time, frequency FROM sunfra_unified_reminders")
rows = cursor.fetchall()
for r in rows:
    print(r)

print("\n=== ALL ROWS IN LOCAL SQLITE sunfra_tasks ===")
cursor.execute("SELECT id, task_name, task_type, assigned_person_name, whatsapp_group_id, due_time, frequency FROM sunfra_tasks")
rows_t = cursor.fetchall()
for r in rows_t:
    print(r)

conn.close()
