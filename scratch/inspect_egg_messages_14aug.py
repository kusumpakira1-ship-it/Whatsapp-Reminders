"""
Find all egg market messages on 14 Aug 2026.
"""
import sys, os, datetime, pymysql
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

target_date = datetime.date(2026, 8, 14)
start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
end_of_day = datetime.datetime.combine(target_date, datetime.time.max)

print(f"=== SEARCHING EGG MESSAGES ON {target_date} ===")

cursor.execute("""
    SELECT sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE (LOWER(raw_text) LIKE '%egg%' OR LOWER(raw_text) LIKE '%kol%' OR LOWER(raw_text) LIKE '%rate%' OR LOWER(raw_text) LIKE '%price%')
      AND timestamp >= %s AND timestamp <= %s 
    ORDER BY timestamp ASC
""", (start_of_day, end_of_day))
raw_msgs = cursor.fetchall()
print(f"Found {len(raw_msgs)} egg market raw_messages on 14 Aug 2026:")

for m in raw_msgs:
    print(f"[{m['timestamp']}] Group: '{m['group_name']}' | Sender: '{m['sender']}'")
    print(f"  Content: {(m['raw_text'] or '')[:300]}")
    print("-" * 60)

conn.close()

