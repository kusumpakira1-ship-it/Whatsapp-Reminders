"""
Inspect all Tasks & Approvals for Gate Manager in the database.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Check tables in MySQL
cursor.execute("SHOW TABLES LIKE '%task%'")
tables = cursor.fetchall()
print("Task Tables:", tables)

# Query sunfra_unified_tasks if present
for t in tables:
    t_name = list(t.values())[0]
    try:
        cursor.execute(f"SELECT * FROM {t_name} WHERE group_id LIKE '%gate%' OR task_name LIKE '%gate%' OR task_name LIKE '%meeting%' OR group_id LIKE '%120363042907512705%'")
        rows = cursor.fetchall()
        print(f"\n--- Rows in {t_name} ({len(rows)} matching) ---")
        for r in rows:
            print(f"ID #{r.get('id')} | Name: {r.get('person_name') or r.get('task_name')} | TaskType: {r.get('task_type')} | Notes: {r.get('task_notes') or r.get('custom_text')} | Freq: {r.get('frequency')} | Due: {r.get('due_time') or r.get('trigger_time')}")
    except Exception as e:
        print(f"Error querying {t_name}: {e}")

