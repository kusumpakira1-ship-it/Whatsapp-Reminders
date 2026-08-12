"""
Debug exact index.php verification logic on Reminder ID 288 (Poornima)
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

# 1. Fetch Reminder 288
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 288")
r = cur.fetchone()

print("=== REMINDER 288 DETAILS ===")
print(f"ID: {r['id']}")
print(f"Person Name : '{r['person_name']}'")
print(f"Person Phone: '{r['person_phone']}'")
print(f"Group JID   : '{r['whatsapp_group_id']}'")
print(f"Report Types: '{r['report_types']}'")
print(f"Task Notes  : '{r['task_notes']}'")
print(f"Status      : '{r['status']}'")

# 2. Fetch raw messages today
cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
raw_messages = cur.fetchall()

print(f"\n=== MATCHING RAW MESSAGES TODAY ({len(raw_messages)} messages) ===")

phones = [p.strip() for p in (r['person_phone'] or '').split(',') if p.strip()]
names = [n.strip() for n in (r['person_name'] or '').split(',') if n.strip()]

def clean_name_string(s):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

for raw_msg in raw_messages:
    raw_text_lower = (raw_msg['raw_text'] or '').lower()
    raw_sender = (raw_msg['sender'] or '').lower()
    raw_group_jid = (raw_msg['whatsapp_group_jid'] or '') if 'whatsapp_group_jid' in raw_msg else ''
    
    sender_matched = False
    for phone in phones:
        clean_phone = ''.join(filter(str.isdigit, phone))
        if clean_phone and (clean_phone in raw_sender or ('91' + clean_phone) in raw_sender):
            sender_matched = True
            break
            
    sender_name_part = clean_name_string(raw_sender.split(' (')[0]) if '(' in raw_sender else clean_name_string(raw_sender)
    name_matched = False
    for name in names:
        t_name = clean_name_string(name)
        if len(sender_name_part) >= 3 and len(t_name) >= 3:
            if t_name in sender_name_part or sender_name_part in t_name:
                name_matched = True
                break
                
    is_poorna_match = ('poorna' in sender_name_part or 'poornima' in sender_name_part or 'poorna' in raw_sender or 'poornima' in raw_sender)
    
    if sender_matched or name_matched or is_poorna_match:
        print(f"  MATCHED SENDER/NAME: [{raw_msg['timestamp']}] Sender: {raw_msg['sender']} | Text: '{raw_msg['raw_text']}'")
        print(f"    sender_matched={sender_matched}, name_matched={name_matched}, is_poorna_match={is_poorna_match}")
        print(f"    sender_name_part='{sender_name_part}', names={names}")
        approval_keywords = ["approved", "approve", "reviewed", "review", "checked", "check", "accepted", "accept", "ok", "verified", "verify", "looks good", "fine", "done"]
        has_app_kw = any(akw in raw_text_lower for akw in approval_keywords)
        print(f"    has_approval_keyword={has_app_kw}")

cur.close()
conn.close()
