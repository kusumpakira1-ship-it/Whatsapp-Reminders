"""
Inspect all messages sent in Jataayu groups on 14 Aug and 15 Aug 2026.
"""
import sys, os, datetime, pymysql
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

print("=== ALL JATAAYU GROUP MESSAGES (14 & 15 AUG 2026) ===")

cursor.execute("""
    SELECT sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE (LOWER(group_name) LIKE '%jataayu%' OR group_name LIKE '%120363428881117777%' OR LOWER(sender) LIKE '%jataayu%')
      AND timestamp >= '2026-08-14 00:00:00'
    ORDER BY timestamp ASC
""")
raw_msgs = cursor.fetchall()
print(f"sunfra_raw_messages count: {len(raw_msgs)}")
for m in raw_msgs:
    print(f"[{m['timestamp']}] From: {m['sender']} | Group: {m['group_name']} | Text: {m['raw_text']}")

cursor.execute("""
    SELECT sender_id, group_id, message_text, timestamp 
    FROM sunfra_whatsapp_messages 
    WHERE (group_id LIKE '%120363428881117777%' OR group_id LIKE '%120363422729608263%')
      AND timestamp >= '2026-08-14 00:00:00'
    ORDER BY timestamp ASC
""")
wa_msgs = cursor.fetchall()
print(f"\nsunfra_whatsapp_messages count: {len(wa_msgs)}")
for m in wa_msgs:
    print(f"[{m['timestamp']}] SenderID: {m['sender_id']} | GroupID: {m['group_id']} | Text: {m['message_text']}")

conn.close()

