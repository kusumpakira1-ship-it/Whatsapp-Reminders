"""
Test matching Aug 13 messages against Reminder 188 (Sunfra Corporate P&L) sub-reports.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Get reminder 188
cursor.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 188")
rem = cursor.fetchone()
print("Reminder 188:", rem)

# Get messages in group 120363425581380088@g.us on 2026-08-13
cursor.execute("""
    SELECT message_text, timestamp FROM sunfra_whatsapp_messages 
    WHERE group_id = '120363425581380088@g.us' AND DATE(timestamp) = '2026-08-13'
""")
msgs = cursor.fetchall()
print("\nAug 13 Messages in Group:", len(msgs))
for m in msgs:
    print(" -", m['message_text'], "at", m['timestamp'])

report_types = [r.strip() for r in rem['report_types'].split(',') if r.strip()]
print("\nRequired Sub-Reports:", report_types)

# Match each sub-report against messages
sub_status = {}
for rep in report_types:
    rep_lower = rep.lower()
    matched = False
    for m in msgs:
        txt = (m['message_text'] or '').lower()
        
        # Matching rules
        if rep_lower == 'day book' and ('day book' in txt or 'daybook' in txt):
            matched = True
        elif rep_lower == 'daily sales' and ('sales' in txt or 'sale' in txt):
            matched = True
        elif rep_lower == 'daily purchases' and ('purchases' in txt or 'purchase' in txt):
            matched = True
        elif rep_lower == 'total payables' and ('payables' in txt or 'payable' in txt):
            matched = True
        elif rep_lower == 'total receivables' and ('receivables' in txt or 'receivable' in txt):
            matched = True
        elif ('p&l' in rep_lower or 'p and l' in rep_lower) and ('p&l' in txt or 'p and l' in txt or 'profit' in txt):
            matched = True
            
        if matched:
            break
            
    sub_status[rep] = 'done' if matched else 'pending'

print("\nResulting Sub-Report Statuses:", json.dumps(sub_status, indent=2))

