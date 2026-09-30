import sys
import pymysql

sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

DB_HOST = "145.223.17.70"
DB_NAME = "u632391467_kusumpakira"
DB_USER = "u632391467_kusumpakira"
DB_PASS = "Kusum@2026Bb!"

conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME)
cursor = conn.cursor()

print("--- Inspecting the MySQL raw messages between Sept 28 19:40 and Sept 29 10:40 ---")
cursor.execute("""
    SELECT id, message_id, sender, group_name, timestamp, created_at, raw_text 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '2026-09-28 19:40:00' AND timestamp <= '2026-09-29 10:40:00'
""")
for r in cursor.fetchall():
    print(f"ID: {r[0]} | TS: {r[4]} | CreatedAt: {r[5]} | Group: {r[3]} | Sender: {r[2]} | Text: {str(r[6])[:80]}")

print("\n--- Hourly breakdown in MySQL sunfra_raw_messages (Sept 28 18:00 to Sept 29 11:00) ---")
cursor.execute("""
    SELECT DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hr, count(*) 
    FROM sunfra_raw_messages
    WHERE timestamp >= '2026-09-28 18:00:00'
    GROUP BY hr ORDER BY hr ASC
""")
for r in cursor.fetchall():
    print(f"MySQL Raw Msg Hour: {r[0]} -> Count: {r[1]}")

conn.close()
