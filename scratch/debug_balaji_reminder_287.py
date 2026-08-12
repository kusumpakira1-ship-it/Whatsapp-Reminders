"""
Debug why Reminder ID 287 (Balaji) is returning is_submitted = True in index.php
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

# 1. Fetch Reminder 287
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 287")
r = cur.fetchone()

print("=== REMINDER 287 DETAILS ===")
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

# 3. Fetch processed data today
cur.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = CURRENT_DATE()")
submissions = cur.fetchall()

def clean_name_string(s):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

phones = [p.strip() for p in (r['person_phone'] or '').split(',') if p.strip()]
names = [n.strip() for n in (r['person_name'] or '').split(',') if n.strip()]

print(f"\n=== MATCHING MESSAGES TODAY FOR BALAJI (ID 287) ===")

is_approval_task = True
approval_keywords = ["approved", "approve", "reviewed", "review", "checked", "check", "accepted", "accept", "ok", "verified", "verify", "looks good", "fine", "done"]

# Check ProcessedData loop in index.php
for sub in submissions:
    sub_sender = (sub['sender'] or '').lower()
    sub_notes = (sub['notes'] or '').lower()
    import re
    raw_s = re.sub(r'^\[.*?\]\s*', '', sub['sender'] or '')
    sender_name_part = clean_name_string(raw_s.split(' (')[0] if '(' in raw_s else raw_s)
    
    sender_matched = False
    for phone in phones:
        clean_phone = "".join(c for c in phone if c.isdigit())
        if clean_phone and (clean_phone in sub_sender or ('91' + clean_phone) in sub_sender):
            sender_matched = True
            break
            
    name_matched = False
    for name in names:
        t_name = clean_name_string(name)
        if len(sender_name_part) >= 3 and len(t_name) >= 3:
            p1 = sender_name_part[:4]
            p2 = t_name[:4]
            if t_name in sender_name_part or sender_name_part in t_name or (p1 and p2 and p1 == p2):
                name_matched = True
                break
                
    if sender_matched or name_matched:
        print(f"  ProcessedData MATCHED: Sender: {sub['sender']} | Notes: '{sub['notes']}'")
        for akw in approval_keywords:
            if akw in sub_notes:
                print(f"    FOUND APPROVAL KEYWORD '{akw}' in ProcessedData!")

# Check RawMessages loop in index.php
for raw_msg in raw_messages:
    raw_text_lower = (raw_msg['raw_text'] or '').lower()
    raw_sender = (raw_msg['sender'] or '').lower()
    import re
    raw_s = re.sub(r'^\[.*?\]\s*', '', raw_msg['sender'] or '')
    sender_name_part = clean_name_string(raw_s.split(' (')[0] if '(' in raw_s else raw_s)
    
    sender_matched = False
    for phone in phones:
        clean_phone = "".join(c for c in phone if c.isdigit())
        if clean_phone and (clean_phone in raw_sender or ('91' + clean_phone) in raw_sender):
            sender_matched = True
            break
            
    name_matched = False
    for name in names:
        t_name = clean_name_string(name)
        if len(sender_name_part) >= 3 and len(t_name) >= 3:
            p1 = sender_name_part[:4]
            p2 = t_name[:4]
            if t_name in sender_name_part or sender_name_part in t_name or (p1 and p2 and p1 == p2):
                name_matched = True
                break
                
    if sender_matched or name_matched:
        print(f"  RawMessage MATCHED: Sender: {raw_msg['sender']} | Text: '{raw_msg['raw_text']}'")
        for akw in approval_keywords:
            if akw in raw_text_lower:
                print(f"    FOUND APPROVAL KEYWORD '{akw}' in RawMessage!")

cur.close()
conn.close()
