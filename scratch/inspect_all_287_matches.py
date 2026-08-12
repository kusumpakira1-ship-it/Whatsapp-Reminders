"""
Inspect all possible matches for Balaji / Reminder 287 in DB today
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

print("=== CHECKING ALL PROCESSED DATA & RAW MESSAGES TODAY ===")

cur.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = CURRENT_DATE()")
proc_rows = cur.fetchall()

print(f"\nProcessed Data today ({len(proc_rows)} rows):")
for p in proc_rows:
    print(f"  Sender: '{p['sender']}' | Group: '{p['group_name']}' | Notes: '{p['notes']}' | Category: '{p['category']}'")

cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
raw_rows = cur.fetchall()

print(f"\nRaw Messages today ({len(raw_rows)} rows):")
balaji_raws = []
for r in raw_rows:
    s = str(r['sender']).lower()
    g = str(r['group_name']).lower()
    t = str(r['raw_text']).lower()
    if 'balaji' in s or 'balaji' in g or '9493928388' in s or 'intern' in g:
        balaji_raws.append(r)

print(f"  Found {len(balaji_raws)} matching raw messages for Balaji/Intern group:")
for r in balaji_raws:
    print(f"    [{r['timestamp']}] Sender: {r['sender']} | Group: {r['group_name']} | Text: '{r['raw_text']}'")

cur.close()
conn.close()
