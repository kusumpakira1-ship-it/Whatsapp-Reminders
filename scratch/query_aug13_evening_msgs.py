"""
Query sunfra_raw_messages and sunfra_whatsapp_messages for Aug 13 between 21:00 and 22:00 IST.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

print("--- sunfra_raw_messages on 2026-08-13 20:00 to 22:00 ---")
cursor.execute("""
    SELECT id, message_id, sender, group_name, timestamp, message_type, raw_text, media_path 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '2026-08-13 20:00:00' AND timestamp <= '2026-08-13 22:00:00'
    ORDER BY timestamp ASC
""")
raw_msgs = cursor.fetchall()
print(f"Count: {len(raw_msgs)}")
for m in raw_msgs:
    print(m)

print("\n--- sunfra_whatsapp_messages on 2026-08-13 20:00 to 22:00 ---")
cursor.execute("""
    SELECT id, message_id, group_id, sender_id, message_text, timestamp 
    FROM sunfra_whatsapp_messages 
    WHERE timestamp >= '2026-08-13 20:00:00' AND timestamp <= '2026-08-13 22:00:00'
    ORDER BY timestamp ASC
""")
wa_msgs = cursor.fetchall()
print(f"Count: {len(wa_msgs)}")
for m in wa_msgs:
    print(m)

