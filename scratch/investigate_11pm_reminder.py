import pymysql
import json
from datetime import datetime

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira',
    cursorclass=pymysql.cursors.DictCursor
)
cur = conn.cursor()

print("--- Row 979 in sunfra_unified_reminders ---")
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 979")
r979 = cur.fetchone()
print(json.dumps(r979, indent=2, default=str))

print("\n--- All reminders scheduled around 23:00 in sunfra_unified_reminders ---")
cur.execute("SELECT id, reminder_type, title, recipient_type, target_group_name, target_group_id, scheduled_time, frequency, is_active, last_sent_at, updated_at FROM sunfra_unified_reminders WHERE scheduled_time LIKE '%23:00%' OR scheduled_time LIKE '%11:00%'")
rows = cur.fetchall()
for row in rows:
    print(json.dumps(row, indent=2, default=str))

print("\n--- Tasks with 'approval' or 'balaji' ---")
cur.execute("SELECT id, task_name, task_type, due_time, repeat_interval, status, completion_details FROM sunfra_tasks WHERE task_name LIKE '%approval%' OR task_name LIKE '%balaji%'")
trows = cur.fetchall()
for row in trows:
    print(json.dumps(row, indent=2, default=str))

print("\n--- Logs in sunfra_reminder_logs on 2026-10-22 around 23:00 ---")
cur.execute("SELECT * FROM sunfra_reminder_logs WHERE created_at >= '2026-10-22 22:45:00' AND created_at <= '2026-10-22 23:30:00'")
lrows = cur.fetchall()
for row in lrows:
    print(json.dumps(row, indent=2, default=str))

print("\n--- Any logs for reminder ID 979 in sunfra_reminder_logs ---")
cur.execute("SELECT * FROM sunfra_reminder_logs WHERE reminder_id = 979 OR task_notes LIKE '%Balaji%' OR message_sent LIKE '%Balaji%' ORDER BY id DESC LIMIT 10")
brows = cur.fetchall()
for row in brows:
    print(json.dumps(row, indent=2, default=str))

conn.close()
