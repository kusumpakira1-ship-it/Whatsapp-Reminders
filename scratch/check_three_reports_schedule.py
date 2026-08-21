"""
Check database sunfra_unified_reminders for Rule Book, Gate Managers, and Feed Formula reminders.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, frequency, repeat_interval, status 
    FROM sunfra_unified_reminders 
    WHERE report_types LIKE '%rule%' OR report_types LIKE '%gate%' OR report_types LIKE '%formula%' OR task_notes LIKE '%rule%' OR task_notes LIKE '%gate%' OR task_notes LIKE '%formula%'
""")
rows = cursor.fetchall()
print("Matching Reminders in DB:")
for r in rows:
    print(f"ID #{r['id']} | Name: {r['person_name']} | Reports: {r['report_types']} | Freq: {r['frequency']} | Status: {r['status']}")

