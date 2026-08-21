"""
Inspect all rows in sunfra_unified_reminders and sunfra_tasks for Today (14 Aug 2026).
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

print("=== SUNFRA UNIFIED REMINDERS ===")
cursor.execute("SELECT id, person_name, person_phone, report_types, trigger_time, status, sub_reports_status FROM sunfra_unified_reminders")
reminders = cursor.fetchall()
for r in reminders:
    print(f"ID: {r['id']} | Name: {r['person_name']} | Phone: {r['person_phone']} | Status: {r['status']}")
    print(f"   Reports: {r['report_types']}")
    print(f"   Sub-Status JSON: {r['sub_reports_status']}")
    print("-" * 60)

print("\n=== SUNFRA TASKS ===")
cursor.execute("SELECT id, task_name, assigned_person_name, due_time, status, completion_keywords, sub_reports_status FROM sunfra_tasks")
tasks = cursor.fetchall()
for t in tasks:
    print(f"ID: {t['id']} | Name: {t['task_name']} | Assigned: {t['assigned_person_name']} | Status: {t['status']}")
    print(f"   Keywords: {t['completion_keywords']}")
    print(f"   Sub-Status JSON: {t['sub_reports_status']}")
    print("-" * 60)

conn.close()

