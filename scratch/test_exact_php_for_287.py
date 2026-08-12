"""
Run exact mirror of verify_reminder_submission for Reminder ID 287
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

cur.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = CURRENT_DATE()")
submissions = cur.fetchall()

def clean_name_string(s):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

phones = [p.strip() for p in (r['person_phone'] or '').split(',') if p.strip()]
names = [n.strip() for n in (r['person_name'] or '').split(',') if n.strip()]

reports = [rep.strip() for rep in (r['report_types'] or '').split(',') if rep.strip()]
if not reports:
    reports = ['Custom Notes']

is_all_submitted = True
submitted_reports = []
missing_reports = []
verification_details = []

for report in reports:
    is_manually_done = False
    report_submitted = False
    
    is_approval_task = (
        'approval' in (r.get('task_notes') or '').lower() or
        'approval' in (r.get('report_types') or '').lower() or
        'approve' in (r.get('task_notes') or '').lower() or
        'review' in (r.get('task_notes') or '').lower() or
        'checked' in (r.get('task_notes') or '').lower()
    )
    
    approval_keywords = ["approved", "approve", "reviewed", "review", "checked", "check", "accepted", "accept", "ok", "verified", "verify", "looks good", "fine", "done"]
    
    raw_keywords = ['Custom Notes', 'Custom', 'Notes']
    
    # 1. Check ProcessedData
    for sub in submissions:
        sub_notes = (sub['notes'] or '').lower()
        raw_s = sub['sender'] or ''
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
        
        if is_approval_task:
            if name_matched:
                for akw in approval_keywords:
                    if akw in sub_notes:
                        report_submitted = True
                        print(f"MATCHED ProcessedData approval: {sub['sender']} -> {sub['notes']}")
                        break
        elif name_matched:
            for kw in raw_keywords:
                if kw.lower() in sub_notes:
                    report_submitted = True
                    print(f"MATCHED ProcessedData generic: {sub['sender']} -> {sub['notes']}")
                    break
                    
    # 2. Check RawMessages
    if not report_submitted:
        for raw_msg in raw_messages:
            raw_text_lower = (raw_msg['raw_text'] or '').lower()
            raw_s = raw_msg['sender'] or ''
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
                        
            if is_approval_task:
                if name_matched:
                    for akw in approval_keywords:
                        if akw in raw_text_lower:
                            report_submitted = True
                            print(f"MATCHED RawMessage approval: {raw_msg['sender']} -> {raw_msg['raw_text']}")
                            break
            elif name_matched:
                for kw in raw_keywords:
                    if kw.lower() in raw_text_lower:
                        report_submitted = True
                        print(f"MATCHED RawMessage generic: {raw_msg['sender']} -> {raw_msg['raw_text']}")
                        break

    if report_submitted:
        submitted_reports.append(report)
    else:
        is_all_submitted = False
        missing_reports.append(report)

print(f"\nFINAL EVALUATION FOR ID 287 (Balaji):")
print(f"is_submitted: {is_all_submitted}")
print(f"submitted_reports: {submitted_reports}")
print(f"missing_reports  : {missing_reports}")

cur.close()
conn.close()
