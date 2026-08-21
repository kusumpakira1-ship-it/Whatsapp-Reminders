"""
Inspect all egg rate messages sent on Aug 13 in MySQL.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("""
    SELECT message_id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE DATE(timestamp) = '2026-08-13'
      AND (raw_text LIKE '%egg%' OR raw_text LIKE '%closing%' OR raw_text LIKE '%ppr%' OR raw_text LIKE '%veh kol%' OR raw_text LIKE '%cc%')
""")
msgs = cursor.fetchall()
print(f"Found {len(msgs)} egg rate messages on Aug 13:")
for m in msgs:
    print(f"\n[{m['timestamp']}] Sender: {m['sender']} | Group: {m['group_name']}")
    print(f"Text:\n{m['raw_text']}\n{'-'*50}")

