"""
Check sunfra_unified_reminders and sunfra_whatsapp_messages for Aug 13.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

print("--- sunfra_unified_reminders for Corporate P&L (Divya / Prajwal) ---")
cursor.execute("SELECT * FROM sunfra_unified_reminders WHERE report_types LIKE '%Sales%' OR report_types LIKE '%P&L%' OR person_name LIKE '%Divya%' OR person_name LIKE '%Prajwal%'")
rows = cursor.fetchall()
for r in rows:
    print(r)

print("\n--- sunfra_reminder_logs for Corporate P&L on Aug 13 ---")
cursor.execute("SELECT * FROM sunfra_reminder_logs WHERE trigger_time LIKE '2026-08-13%' OR executed_at LIKE '2026-08-13%' ORDER BY id DESC")
rows = cursor.fetchall()
for r in rows:
    if 'P&L' in str(r) or 'Divya' in str(r) or 'Prajwal' in str(r) or 'Sales' in str(r) or 'Day Book' in str(r):
        print(r)

