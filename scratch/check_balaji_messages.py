"""
Check messages for Balaji (9493928388) and group Balaji Team on Aug 13 and Aug 14.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Check whatsapp messages for Balaji (9493928388) on Aug 13 and Aug 14
cursor.execute("""
    SELECT message_id, group_id, sender_id, message_text, timestamp 
    FROM sunfra_whatsapp_messages 
    WHERE (sender_id LIKE '%9493928388%' OR group_id LIKE '%Balaji%' OR message_text LIKE '%Balaji%')
      AND DATE(timestamp) IN ('2026-08-13', '2026-08-14')
    ORDER BY timestamp ASC
""")
messages = cursor.fetchall()
print(f"Found {len(messages)} sunfra_whatsapp_messages for Balaji / 9493928388 on Aug 13 & 14:")
for m in messages:
    print(f"  [{m['timestamp']}] Sender: {m['sender_id']} | Group: {m['group_id']} | Text: {m['message_text']}")

# Check raw_messages as well
cursor.execute("""
    SELECT message_id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE (sender LIKE '%9493928388%' OR group_name LIKE '%Balaji%' OR raw_text LIKE '%Balaji%')
      AND DATE(timestamp) IN ('2026-08-13', '2026-08-14')
    ORDER BY timestamp ASC
""")
raw_msgs = cursor.fetchall()
print(f"\nFound {len(raw_msgs)} sunfra_raw_messages for Balaji / 9493928388 on Aug 13 & 14:")
for rm in raw_msgs:
    print(f"  [{rm['timestamp']}] Sender: {rm['sender']} | Group: {rm['group_name']} | Text: {rm['raw_text']}")

# Also check reminder #287 or reminder details for Balaji
cursor.execute("SELECT * FROM sunfra_unified_reminders WHERE person_name LIKE '%Balaji%' OR person_phone LIKE '%9493928388%'")
rems = cursor.fetchall()
print("\nBalaji Reminders in DB:")
for r in rems:
    print(f"  ID #{r['id']} | Name: {r['person_name']} | Phone: {r['person_phone']} | Group: {r['whatsapp_group_id']} | Reports: {r['report_types']} | Notes: {r['task_notes']}")

