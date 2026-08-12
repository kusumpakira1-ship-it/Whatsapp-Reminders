import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute('SELECT * FROM sunfra_unified_reminders')
rows = cur.fetchall()

print(f"=== HOSTINGER MYSQL UNIFIED REMINDERS ({len(rows)} rows) ===\n")
for r in rows:
    rt = str(r.get('report_types') or '').lower()
    tn = str(r.get('task_notes') or '').lower()
    ph = str(r.get('person_phone') or '')
    if 'meeting' in rt or 'meeting' in tn or '1234567890' in ph:
        print(f"ID: {r['id']} | Group: {r['whatsapp_group_id']} | Person: {r['person_name']} | Phone: {r['person_phone']} | Status: {r['status']}")
        print(f"  Trigger     : {r['trigger_time']}")
        print(f"  Report Types: {r['report_types']}")
        print(f"  Task Notes  : {r['task_notes']}")
        print("-" * 60)

cur.close()
conn.close()
