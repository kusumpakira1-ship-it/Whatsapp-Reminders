"""
Check messages sent in target Rule Book group JID 120363430772426306@g.us on Aug 13.
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
    SELECT message_id, group_id, sender_id, message_text, timestamp 
    FROM sunfra_whatsapp_messages 
    WHERE group_id = '120363430772426306@g.us'
      AND DATE(timestamp) = '2026-08-13'
    ORDER BY timestamp ASC
""")
msgs = cursor.fetchall()
print(f"Messages in Rule Book group (120363430772426306@g.us) on Aug 13: {len(msgs)}")
for m in msgs:
    print(f"  [{m['timestamp']}] Sender: {m['sender_id']} | Text: {m['message_text']}")

