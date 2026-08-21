"""
Verify Chick mortality in supervisor messages for 14 & 15 Aug 2026.
"""
import pymysql, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("""
    SELECT raw_text, timestamp, sender 
    FROM sunfra_raw_messages 
    WHERE (LOWER(raw_text) LIKE '%%mortality%%' OR LOWER(raw_text) LIKE '%%chick%%')
      AND timestamp >= '2026-08-14 00:00:00'
    ORDER BY timestamp ASC
""")
msgs = cursor.fetchall()

print(f"=== MORTALITY MESSAGES (14 & 15 AUG 2026) ({len(msgs)} msgs) ===")
for m in msgs:
    print(f"\n[{m['timestamp']}] Sender: {m['sender']}")
    print("Raw Text:\n", m['raw_text'])
    print("-" * 60)

conn.close()

