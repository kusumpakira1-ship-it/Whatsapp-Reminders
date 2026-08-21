"""
Simulate backend verify_reminder_submission for Reminder 188 on Aug 13.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Fetch reminder 188
cursor.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 188")
r = cursor.fetchone()

# Fetch Aug 13 messages in group 120363425581380088@g.us
cursor.execute("""
    SELECT message_text, timestamp, sender_id 
    FROM sunfra_whatsapp_messages 
    WHERE group_id = '120363425581380088@g.us' AND DATE(timestamp) = '2026-08-13'
""")
wa_msgs = cursor.fetchall()

reports = [rep.strip() for rep in (r['report_types'] or '').split(',') if rep.strip()]

# Calculate sub-report status map dynamically
dynamic_sub_status = {}
db_sub_status = {}
if r['sub_reports_status']:
    try:
        db_sub_status = json.loads(r['sub_reports_status'])
    except:
        pass

for rep in reports:
    rep_lower = rep.lower()
    # Check if manually set in DB
    if db_sub_status.get(rep) == 'done':
        dynamic_sub_status[rep] = 'done'
        continue
    if db_sub_status.get(rep) == 'pending':
        dynamic_sub_status[rep] = 'pending'
        continue
        
    # Auto-match from WhatsApp messages
    matched = False
    for m in wa_msgs:
        txt = (m['message_text'] or '').lower()
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
            
    dynamic_sub_status[rep] = 'done' if matched else 'pending'

print("Dynamic Sub Status for Aug 13:", json.dumps(dynamic_sub_status, indent=2))
print("All reports done?:", all(v == 'done' for v in dynamic_sub_status.values()))

