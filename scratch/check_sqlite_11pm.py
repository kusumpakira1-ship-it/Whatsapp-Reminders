import sqlite3, json

conn = sqlite3.connect('backend/whatsapp_reminders.sqlite')
cur = conn.cursor()

print("=== Row 979 in sunfra_unified_reminders ===")
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 979")
row = cur.fetchone()
col_names = [d[0] for d in cur.description]
if row:
    print(json.dumps(dict(zip(col_names, row)), indent=2, default=str))
else:
    print("Row 979 not found!")

print("\n=== Reminders with 23:00 or 11:00 in sunfra_unified_reminders ===")
cur.execute("SELECT id, reminder_type, title, recipient_type, target_group_name, target_group_id, scheduled_time, frequency, is_active, last_sent_at, updated_at FROM sunfra_unified_reminders WHERE scheduled_time LIKE '%23:00%' OR scheduled_time LIKE '%11:00%'")
for r in cur.fetchall():
    print(r)

print("\n=== All Reminders in sunfra_unified_reminders ===")
cur.execute("SELECT id, reminder_type, title, scheduled_time, frequency, is_active, last_sent_at FROM sunfra_unified_reminders")
for r in cur.fetchall():
    print(r)

print("\n=== Tasks in sunfra_tasks with balaji or approval ===")
cur.execute("SELECT id, task_name, task_type, due_time, repeat_interval, status, completion_details FROM sunfra_tasks WHERE task_name LIKE '%approval%' OR task_name LIKE '%balaji%'")
for r in cur.fetchall():
    print(r)

conn.close()
