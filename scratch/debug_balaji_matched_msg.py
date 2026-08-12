"""
Debug exact raw message matching in index.php for Reminder 287 (Balaji)
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

cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 287")
r = cur.fetchone()

cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
raw_messages = cur.fetchall()

raw_keywords = ['Custom Notes', 'Custom', 'Notes']

print(f"=== CHECKING WHY BALAJI (ID 287) MATCHED A RAW MESSAGE ===")

for raw_msg in raw_messages:
    raw_text_lower = (raw_msg['raw_text'] or '').lower()
    raw_group_jid = raw_msg.get('whatsapp_group_jid') or ''
    
    # Check if group matched
    clean_raw_group_jid = raw_group_jid.replace('@g.us', '')
    clean_target_group_jid = (r['whatsapp_group_id'] or '').replace('@g.us', '')
    
    group_matched = False
    if clean_target_group_jid and (clean_raw_group_jid == clean_target_group_jid or 'balaji' in (raw_msg['group_name'] or '').lower()):
        group_matched = True
        
    if group_matched:
        for kw in raw_keywords:
            if kw.lower() in raw_text_lower:
                print(f"  MATCHED GROUP MSG: [{raw_msg['timestamp']}] Sender: {raw_msg['sender']} | Text: '{raw_msg['raw_text']}'")
                print(f"    Matched keyword: '{kw}'!")

cur.close()
conn.close()
