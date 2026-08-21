"""
Search for Birds Weight data in WhatsApp messages and DB tables for Aug 13, 14, 15 2026.
"""
import pymysql, sys, datetime, re
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

print("=== 1. SEARCHING WHATSAPP RAW MESSAGES FOR 'WEIGHT' OR 'HEN' OR 'WT' OR 'GRAM' ===")

cursor.execute("""
    SELECT sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE (LOWER(raw_text) LIKE '%%weight%%' OR LOWER(raw_text) LIKE '%%hen%%' OR LOWER(raw_text) LIKE '%%gram%%' OR LOWER(raw_text) LIKE '%%wt%%')
      AND timestamp >= '2026-08-01 00:00:00'
    ORDER BY timestamp DESC
    LIMIT 30
""")
msgs = cursor.fetchall()
print(f"Found {len(msgs)} weight-related messages in August:")
for m in msgs:
    print(f"[{m['timestamp']}] Group: '{m['group_name']}' | Sender: '{m['sender']}'")
    print(f"  Content: {(m['raw_text'] or '')[:250]}")
    print("-" * 60)

print("\n=== 2. SEARCHING SUNFRA_PROCESSED_DATA FOR 'HEN_WEIGHT' OR WEIGHT DATA ===")
cursor.execute("""
    SELECT * FROM sunfra_processed_data
    WHERE category IN ('hen_weight', 'weight') OR average_weight IS NOT NULL
    ORDER BY id DESC
    LIMIT 20
""")
prows = cursor.fetchall()
print(f"Found {len(prows)} rows in sunfra_processed_data:")
for r in prows:
    print(r)

conn.close()

