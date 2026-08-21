"""
Inspect all past messages in the Gate Manager group (120363225998735559@g.us) to find real-world meeting report phrasing, typos, and short forms.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Query sunfra_raw_messages for Gate Manager group over all time
cursor.execute("""
    SELECT message_id, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE group_name LIKE '%Gate%' OR raw_text LIKE '%meeting%' OR raw_text LIKE '%follow%' OR raw_text LIKE '%shed%' OR raw_text LIKE '%worker%'
    ORDER BY timestamp DESC
    LIMIT 100
""")
raw_msgs = cursor.fetchall()
print(f"Found {len(raw_msgs)} recent messages related to Gate / Meetings / Workers in sunfra_raw_messages:")
for rm in raw_msgs:
    txt = (rm['raw_text'] or '').strip()
    if txt and len(txt) > 3:
        print(f"[{rm['timestamp']}] {rm['sender']}: {txt[:200]}")

