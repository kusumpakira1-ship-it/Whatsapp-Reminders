"""
Inspect all raw messages received TODAY (14 Aug 2026) in MySQL.
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
    WHERE DATE(timestamp) = '2026-08-14'
    ORDER BY timestamp ASC
""")
msgs = cursor.fetchall()
print(f"Total raw messages received TODAY (14 Aug 2026) so far: {len(msgs)}")
for m in msgs:
    txt = (m['raw_text'] or '').strip().replace('\n', ' ')
    print(f"  [{m['timestamp']}] Group: '{m['group_name']}' | Sender: '{m['sender']}' | Text: '{txt[:120]}'")

