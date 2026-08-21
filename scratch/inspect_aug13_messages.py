"""
Inspect sunfra_raw_messages, sunfra_whatsapp_messages, and sunfra_processed_data for 2026-08-13.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

print("--- sunfra_raw_messages ---")
cursor.execute("SELECT * FROM sunfra_raw_messages WHERE timestamp LIKE '2026-08-13%' OR created_at LIKE '2026-08-13%' ORDER BY id DESC LIMIT 20")
rows = cursor.fetchall()
print(f"Count: {len(rows)}")
for r in rows:
    print(r)

print("\n--- sunfra_whatsapp_messages ---")
cursor.execute("SELECT * FROM sunfra_whatsapp_messages WHERE timestamp LIKE '2026-08-13%' OR created_at LIKE '2026-08-13%' ORDER BY id DESC LIMIT 20")
rows = cursor.fetchall()
print(f"Count: {len(rows)}")
for r in rows:
    print(r)

print("\n--- sunfra_processed_data ---")
cursor.execute("SELECT * FROM sunfra_processed_data WHERE date LIKE '2026-08-13%' OR timestamp LIKE '2026-08-13%' ORDER BY id DESC LIMIT 20")
rows = cursor.fetchall()
print(f"Count: {len(rows)}")
for r in rows:
    print(r)

