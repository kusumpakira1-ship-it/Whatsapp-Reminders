"""
Check database for Balaji's reminders and messages sent today (12 Aug 2026) around 9:00 AM
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

print("=== CHECKING BALAJI REMINDERS & MESSAGES IN DATABASE TODAY ===\n")

# 1. Fetch all reminders for Balaji
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE LOWER(person_name) LIKE '%balaji%' OR LOWER(report_types) LIKE '%balaji%' OR person_phone LIKE '%9008349756%' OR person_phone LIKE '%8985779911%' OR whatsapp_group_id LIKE '%120363406924564250%'")
reminders = cur.fetchall()

print(f"Found {len(reminders)} reminders for Balaji:")
for r in reminders:
    print(f"  ID: {r['id']} | Group: {r['whatsapp_group_id']} | Person: {r['person_name']} ({r['person_phone']}) | Trigger: {r['trigger_time']} | Status: {r['status']}")
    print(f"  Report Types: {r['report_types']}")
    print(f"  Task Notes  : {r['task_notes']}")
    print("-" * 60)

# 2. Fetch all raw messages today for Balaji / Balaji group
cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE() AND (LOWER(sender) LIKE '%balaji%' OR LOWER(group_name) LIKE '%balaji%' OR LOWER(group_name) LIKE '%intern%' OR LOWER(group_name) LIKE '%team%')")
raw_msgs = cur.fetchall()

print(f"\nFound {len(raw_msgs)} raw messages for Balaji today:")
for m in raw_msgs:
    print(f"  [{m['timestamp']}] Sender: {m['sender']} | Group: {m['group_name']} | Text: '{m['raw_text']}'")

# 3. Fetch all raw messages sent by anyone in Balaji group or direct today
cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE() AND (LOWER(raw_text) LIKE '%balaji%' OR LOWER(sender) LIKE '%balaji%')")
sender_msgs = cur.fetchall()

print(f"\nFound {len(sender_msgs)} messages matching Balaji sender/text today:")
for m in sender_msgs:
    print(f"  [{m['timestamp']}] Sender: {m['sender']} | Group: {m['group_name']} | Text: '{m['raw_text']}'")

cur.close()
conn.close()
