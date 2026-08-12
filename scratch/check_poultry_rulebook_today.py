"""
Check DB submissions for Accounts Poultry and Rule Book today (12 Aug 2026)
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

print("=== CHECKING DB SUBMISSIONS TODAY (12 AUG 2026) ===\n")

# 1. Accounts Poultry Reminder ID 185
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 185 OR person_name LIKE '%Mahalakshmi%' OR whatsapp_group_id LIKE '%120363042907512705%'")
rem_poultry = cur.fetchall()
print("Accounts Poultry Reminder in DB:")
for r in rem_poultry:
    print(f"  ID: {r['id']} | Group: {r['whatsapp_group_id']} | Person: {r['person_name']} | Trigger: {r['trigger_time']} | Status: {r['status']}")
    print(f"  Report Types: {r['report_types']}")

# 2. Rule Book Reminder ID 213
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 213 OR whatsapp_group_id LIKE '%120363430772426306%'")
rem_rule = cur.fetchall()
print("\nRule Book Reminder in DB:")
for r in rem_rule:
    print(f"  ID: {r['id']} | Group: {r['whatsapp_group_id']} | Person: {r['person_name']} | Trigger: {r['trigger_time']} | Status: {r['status']}")
    print(f"  Report Types: {r['report_types']}")

# 3. Check Processed Data today
cur.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = CURRENT_DATE()")
proc_today = cur.fetchall()
print(f"\nProcessed Data rows today ({len(proc_today)} total):")
for p in proc_today:
    print(f"  Sender: {p['sender']} | Group: {p['group_name']} | Category: {p['category']} | Notes: '{p['notes']}'")

# 4. Check Raw Messages in Accounts Poultry group or Rule Book group today
cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE() AND (group_name LIKE '%Poultry%' OR group_name LIKE '%Rule%' OR sender LIKE '%Mahalakshmi%' OR raw_text LIKE '%rule%' OR raw_text LIKE '%day book%' OR raw_text LIKE '%ca statement%')")
raw_today = cur.fetchall()
print(f"\nRaw Messages matching Poultry / Rule Book today ({len(raw_today)} total):")
for m in raw_today:
    print(f"  [{m['timestamp']}] Sender: {m['sender']} | Group: {m['group_name']} | Text: '{m['raw_text']}'")

cur.close()
conn.close()
