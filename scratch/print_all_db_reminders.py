import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, status FROM sunfra_unified_reminders")
rows = cur.fetchall()

print(f"=== ALL REMINDERS IN DATABASE ({len(rows)} rows) ===")
for r in rows:
    print(f"ID: {r['id']} | Person: {r['person_name']} | Group: {r['whatsapp_group_id']} | Status: '{r['status']}' | Notes: '{r['task_notes']}'")

cur.close()
conn.close()
