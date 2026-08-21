"""
Check all active reminders against Aug 13 WhatsApp messages and update sub_reports_status for any matching submissions.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Fetch all reminders
cursor.execute("SELECT * FROM sunfra_unified_reminders")
reminders = cursor.fetchall()

# Fetch all Aug 13 messages
cursor.execute("SELECT group_id, sender_id, message_text, timestamp FROM sunfra_whatsapp_messages WHERE DATE(timestamp) = '2026-08-13'")
wa_msgs = cursor.fetchall()

print(f"Total Reminders: {len(reminders)}, Total Aug 13 Messages: {len(wa_msgs)}")

for r in reminders:
    report_types = [rep.strip() for rep in (r['report_types'] or '').split(',') if rep.strip()]
    if not report_types:
        continue
        
    gid = (r['whatsapp_group_id'] or '').strip()
    # Filter messages for this reminder's group if set
    group_msgs = [m for m in wa_msgs if m['group_id'] == gid] if gid else wa_msgs
    
    sub_status = {}
    if r['sub_reports_status']:
        try:
            sub_status = json.loads(r['sub_reports_status'])
        except:
            pass
            
    updated = False
    for rep in report_types:
        rep_lower = rep.lower()
        if sub_status.get(rep) == 'done':
            continue
            
        matched = False
        for m in group_msgs:
            txt = (m['message_text'] or '').lower()
            if not txt: continue
            
            if 'day book' in rep_lower and ('day book' in txt or 'daybook' in txt or 'day_book' in txt):
                matched = True
            elif 'sales' in rep_lower and ('sales' in txt or 'sale' in txt):
                matched = True
            elif 'purchases' in rep_lower and ('purchases' in txt or 'purchase' in txt):
                matched = True
            elif 'payables' in rep_lower and ('payables' in txt or 'payable' in txt):
                matched = True
            elif 'receivables' in rep_lower and ('receivables' in txt or 'receivable' in txt):
                matched = True
            elif ('p&l' in rep_lower or 'p and l' in rep_lower or 'profit' in rep_lower) and ('p&l' in txt or 'p and l' in txt or 'profit' in txt):
                matched = True
            elif 'work update' in rep_lower and ('update' in txt or 'work' in txt or 'report' in txt):
                matched = True
            elif rep_lower in txt:
                matched = True
                
            if matched:
                sub_status[rep] = 'done'
                updated = True
                break
                
    if updated:
        json_str = json.dumps(sub_status)
        cursor.execute("UPDATE sunfra_unified_reminders SET sub_reports_status = %s WHERE id = %s", (json_str, r['id']))
        conn.commit()
        print(f"Updated Reminder #{r['id']} ({r['person_name']} - {r['whatsapp_group_id']}):", json_str)

