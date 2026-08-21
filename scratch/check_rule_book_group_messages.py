"""
Check messages in Rule Book group for Aug 13.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Check Reminder #213 details
cursor.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 213 OR report_types LIKE '%rule%'")
rems = cursor.fetchall()
print("Rule Book Reminders:")
for r in rems:
    print(f"ID #{r['id']} | Group: {r['whatsapp_group_id']} | Reports: {r['report_types']} | Notes: {r['task_notes']}")
    gid = r['whatsapp_group_id']

# Check sunfra_whatsapp_messages for Rule Book group on Aug 13
cursor.execute("""
    SELECT message_id, group_id, sender_id, message_text, timestamp 
    FROM sunfra_whatsapp_messages 
    WHERE group_id = '120363042907512705@g.us'
      AND DATE(timestamp) = '2026-08-13'
    ORDER BY timestamp ASC
""")
msgs = cursor.fetchall()
print(f"\nSunfra WhatsApp Messages in Rule Book group (120363042907512705@g.us) on Aug 13: {len(msgs)}")
for m in msgs:
    print(f"  [{m['timestamp']}] Sender: {m['sender_id']} | Text: {m['message_text']}")

# Check sunfra_raw_messages for Rule Book group on Aug 13
cursor.execute("""
    SELECT message_id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE (group_name LIKE '%Rule%' OR group_name LIKE '%rule%')
      AND DATE(timestamp) = '2026-08-13'
    ORDER BY timestamp ASC
""")
raw_msgs = cursor.fetchall()
print(f"\nSunfra Raw Messages in Rule Book group on Aug 13: {len(raw_msgs)}")
for rm in raw_msgs:
    print(f"  [{rm['timestamp']}] Sender: {rm['sender']} | Text: {rm['raw_text']}")

