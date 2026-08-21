"""
Inspect table schemas for sunfra_whatsapp_messages, sunfra_reminder_logs, and sunfra_tasks.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

for tname in ['sunfra_whatsapp_messages', 'sunfra_reminder_logs', 'sunfra_tasks', 'sunfra_unified_reminders']:
    cursor.execute(f"DESCRIBE {tname}")
    cols = cursor.fetchall()
    print(f"\n=== SCHEMA FOR {tname} ===")
    for c in cols:
        print(f"  {c['Field']} ({c['Type']})")

cursor.execute("SELECT * FROM sunfra_whatsapp_messages WHERE DATE(timestamp) = CURRENT_DATE() LIMIT 5")
rows = cursor.fetchall()
print("\n=== SAMPLE RAW MESSAGES TODAY ===")
for r in rows:
    print(r)

conn.close()

