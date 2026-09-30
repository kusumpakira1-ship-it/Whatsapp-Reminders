import sqlite3
import os
import sys

# force stdout to utf-8 if possible
sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

db_path = os.path.join("backend", "whatsapp_reminders.sqlite")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- 1. Checking sunfra_raw_messages after 2026-09-28 20:00:00 ---")
cursor.execute("""
    SELECT id, message_id, sender, group_name, timestamp, created_at, raw_text 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '2026-09-28 20:00:00' 
    ORDER BY timestamp ASC
""")
raw_msgs = cursor.fetchall()
print(f"Raw messages found after 8 PM yesterday: {len(raw_msgs)}")
for r in raw_msgs:
    text_snippet = str(r[6])[:60].replace('\n', ' ')
    print(f"ID: {r[0]} | TS: {r[4]} | CreatedAt: {r[5]} | Group: {r[3]} | Text: {text_snippet}")

print("\n--- 2. Hourly breakdown of sunfra_raw_messages (Sept 28 08:00 to Sept 29 11:00) ---")
cursor.execute("""
    SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hr, count(*), max(created_at)
    FROM sunfra_raw_messages
    WHERE timestamp >= '2026-09-28 08:00:00'
    GROUP BY hr
    ORDER BY hr ASC
""")
for row in cursor.fetchall():
    print(f"Hour: {row[0]} -> Raw Msg Count: {row[1]}, Max created_at: {row[2]}")

print("\n--- 3. Hourly breakdown of sunfra_whatsapp_messages ---")
cursor.execute("""
    SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as hr, count(*)
    FROM sunfra_whatsapp_messages
    WHERE timestamp >= '2026-09-28 08:00:00'
    GROUP BY hr
    ORDER BY hr ASC
""")
for row in cursor.fetchall():
    print(f"Hour: {row[0]} -> Processed Msg Count: {row[1]}")

print("\n--- 4. Max timestamp/created_at across all tables in backend/whatsapp_reminders.sqlite ---")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
for table in sorted(tables):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cursor.fetchall()]
    time_cols = [c for c in cols if 'time' in c.lower() or 'created' in c.lower() or 'updated' in c.lower() or 'date' in c.lower()]
    for tcol in time_cols:
        try:
            cursor.execute(f"SELECT MAX({tcol}) FROM {table}")
            mval = cursor.fetchone()[0]
            if mval:
                print(f"Table [{table:35s}] col [{tcol:20s}] max value: {mval}")
        except Exception as e:
            pass

conn.close()
