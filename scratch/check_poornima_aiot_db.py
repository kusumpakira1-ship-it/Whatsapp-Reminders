"""
Check raw messages and processed data for Poornima (7204484516) or AIoT Alliance group today
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

print("=== CHECKING MESSAGES TODAY FOR POORNIMA / AIOT ALLIANCE ===\n")

# 1. Fetch raw messages today
cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
raw_msgs = cur.fetchall()

print(f"Total raw messages today: {len(raw_msgs)}")

aiot_poornima_msgs = []
for m in raw_msgs:
    sender = str(m.get('sender') or '')
    group_name = str(m.get('group_name') or '')
    text = str(m.get('raw_text') or '')
    
    if '7204484516' in sender or 'poornima' in sender.lower() or 'aiot' in group_name.lower() or 'alliance' in group_name.lower():
        aiot_poornima_msgs.append(m)

print(f"\nFound {len(aiot_poornima_msgs)} raw messages for Poornima / AIoT Alliance today:")
for m in aiot_poornima_msgs:
    print(f"  [{m['timestamp']}] Sender: {m['sender']} | Group: {m['group_name']} | Text: {m['raw_text']}")

# 2. Check Processed Data today
cur.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = CURRENT_DATE()")
proc_msgs = cur.fetchall()

print(f"\nFound {len(proc_msgs)} ProcessedData rows today:")
for p in proc_msgs:
    sender = str(p.get('sender') or '')
    group_name = str(p.get('group_name') or '')
    if '7204484516' in sender or 'poornima' in sender.lower() or 'aiot' in group_name.lower() or 'alliance' in group_name.lower():
        print(f"  ProcessedData: {p['sender']} | Group: {p['group_name']} | Notes: {p['notes']} | Category: {p['category']}")

# 3. Check exact Approval Task reminder details in DB
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE person_phone LIKE '%7204484516%' OR whatsapp_group_id LIKE '%120363428008153650%'")
reminders = cur.fetchall()
print(f"\nFound {len(reminders)} Reminders in DB for Poornima / AIoT Alliance:")
for r in reminders:
    print(f"  ID: {r['id']} | Group: {r['whatsapp_group_id']} | Person: {r['person_name']} ({r['person_phone']}) | Trigger: {r['trigger_time']} | Status: {r['status']}")
    print(f"  Report Types: {r['report_types']}")
    print(f"  Task Notes  : {r['task_notes']}")

cur.close()
conn.close()
