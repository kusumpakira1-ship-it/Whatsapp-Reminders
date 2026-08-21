"""
Inspect escalation report logs and DB logs for 9:30 PM and 11:59 PM yesterday (13 Aug).
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Check escalation tables if any exist
cursor.execute("SHOW TABLES LIKE '%escalation%'")
tables = cursor.fetchall()
print("Escalation Tables:", tables)

# Check reminder logs for yesterday (2026-08-13)
cursor.execute("""
    SELECT * FROM sunfra_reminder_logs 
    WHERE DATE(executed_at) = '2026-08-13'
    ORDER BY executed_at ASC
""")
logs = cursor.fetchall()
print(f"\nTotal Reminder Logs on Aug 13: {len(logs)}")
for l in logs:
    print(f"  ID #{l.get('reminder_id')} | Time: {l.get('executed_at')} | Status: {l.get('status')} | Notes: {l.get('notes')}")

# Check reminder #287 and #263 in unified_reminders
cursor.execute("SELECT * FROM sunfra_unified_reminders WHERE person_name LIKE '%Balaji%' OR whatsapp_group_id = '120363406924564250@g.us'")
rems = cursor.fetchall()
print("\nBalaji Team Reminders in DB:")
for r in rems:
    print(f"  ID #{r['id']} | Name: {r['person_name']} | Group: {r['whatsapp_group_id']} | Status: {r['status']} | Reports: {r['report_types']}")

