import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT * FROM sunfra_tasks WHERE id >= 95 ORDER BY id ASC")
rows = cur.fetchall()

print(f"=== TASKS INSIDE DB (ID >= 95) ({len(rows)} rows) ===")
for r in rows:
    print(f"ID: {r['id']} | Task Name: {r['task_name']} | Type: {r['task_type']} | Assignee: {r['assigned_person_name']} | Group: {r['whatsapp_group_id']}")
    print(f"  Due Time: {r['due_time']} | Created At: {r['created_at']} | Keywords: {r['completion_keywords']}")
    print("-" * 70)

cur.close()
conn.close()
