"""
Check all raw messages and processed data for group 120363406924564250@g.us today
"""

import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

print("=== CHECKING MESSAGES IN BALAJI TEAM GROUP TODAY ===")

cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
raws = cur.fetchall()

print(f"Total raw messages today: {len(raws)}")

group_msgs = []
for r in raws:
    gname = str(r['group_name'] or '').lower()
    text = str(r['raw_text'] or '').lower()
    sender = str(r['sender'] or '').lower()
    
    if 'balaji' in gname or 'intern' in gname or 'balaji' in sender or '9493928388' in sender:
        group_msgs.append(r)

print(f"Found {len(group_msgs)} raw messages for Balaji/Group today:")
for m in group_msgs:
    print(f"  [{m['timestamp']}] Sender: {m['sender']} | Group: {m['group_name']} | Text: '{m['raw_text']}'")

# Check if there are raw messages with group JID 120363406924564250 in sunfra_whatsapp_messages
cur.execute("""
    SELECT r.*, w.group_id 
    FROM sunfra_raw_messages r 
    JOIN sunfra_whatsapp_messages w ON r.message_id = w.message_id 
    WHERE DATE(r.timestamp) = CURRENT_DATE() AND w.group_id LIKE '%120363406924564250%'
""")
w_msgs = cur.fetchall()
print(f"\nFound {len(w_msgs)} raw messages linked via sunfra_whatsapp_messages to JID 120363406924564250 today:")
for m in w_msgs:
    print(f"  [{m['timestamp']}] Sender: {m['sender']} | Group JID: {m['group_id']} | Text: '{m['raw_text']}'")

cur.close()
conn.close()
