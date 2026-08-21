"""
Check raw messages and processed data for Rule Book and Gate keywords on Aug 13.
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
    SELECT message_id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE DATE(timestamp) = '2026-08-13'
      AND (raw_text LIKE '%rule%' OR raw_text LIKE '%gate%' OR raw_text LIKE '%entry%' OR group_name LIKE '%rule%' OR group_name LIKE '%gate%')
""")
raw_msgs = cursor.fetchall()
print("Aug 13 Raw Messages matching Rule / Gate / Entry:")
for rm in raw_msgs:
    print(f"[{rm['timestamp']}] Sender: {rm['sender']} | Group: {rm['group_name']} | Text: {rm['raw_text'][:150]}")

