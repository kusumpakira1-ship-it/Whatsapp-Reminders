"""
Run PHP CLI locally to execute verify_reminder_submission for Reminder ID 288
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

cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 288")
r = cur.fetchone()

cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
raw_messages = cur.fetchall()

print(f"=== TESTING VERIFICATION FOR REMINDER 288 ===")
print(f"ID: {r['id']} | Person: {r['person_name']} | Report Types: '{r['report_types']}'")

reports = [rep.strip() for rep in (r['report_types'] or '').split(',') if rep.strip()]
if not reports:
    reports = ['Custom Notes']

print(f"Reports evaluated: {reports}")

phones = [p.strip() for p in (r['person_phone'] or '').split(',') if p.strip()]
names = [n.strip() for n in (r['person_name'] or '').split(',') if n.strip()]

def clean_name_string(s):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

is_approval_task = True
approval_keywords = ["approved", "approve", "reviewed", "review", "checked", "check", "accepted", "accept", "ok", "verified", "verify", "looks good", "fine", "done"]

report_submitted = False
report_match_msg = ""

for raw_msg in raw_messages:
    raw_text_lower = (raw_msg['raw_text'] or '').lower()
    import re
    raw_s = re.sub(r'^\[.*?\]\s*', '', raw_msg['sender'] or '')
    sender_name_part = clean_name_string(raw_s.split(' (')[0] if '(' in raw_s else raw_s)
    
    name_matched = False
    for name in names:
        t_name = clean_name_string(name)
        if len(sender_name_part) >= 3 and len(t_name) >= 3:
            p1 = sender_name_part[:4]
            p2 = t_name[:4]
            if t_name in sender_name_part or sender_name_part in t_name or (p1 and p2 and p1 == p2):
                name_matched = True
                break
                
    if name_matched:
        for akw in approval_keywords:
            if akw in raw_text_lower:
                report_submitted = True
                report_match_msg = f"Approved via raw WhatsApp message by assigned manager {raw_msg['sender']}"
                break
        if report_submitted:
            break

print(f"Result: report_submitted={report_submitted}, details='{report_match_msg}'")

cur.close()
conn.close()
