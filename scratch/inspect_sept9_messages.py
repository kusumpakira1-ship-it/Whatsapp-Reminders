import sqlite3
import json
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

db_path = "backend/whatsapp_reminders.sqlite"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- INSPECTING MESSAGES FOR 09 SEP 2026 ---")

# Check table structure for saved messages
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Let's inspect all records in messages or chat_messages table if exists
for tbl in tables:
    tname = tbl[0]
    if "msg" in tname or "message" in tname or "log" in tname or "event" in tname or "remind" in tname:
        print(f"\n--- Table: {tname} ---")
        try:
            cursor.execute(f"PRAGMA table_info({tname});")
            cols = [c[1] for c in cursor.fetchall()]
            print("Columns:", cols)
            
            cursor.execute(f"SELECT * FROM {tname} ORDER BY id DESC LIMIT 10")
            rows = cursor.fetchall()
            print(f"Total sample rows ({len(rows)}):")
            for r in rows:
                print(r)
        except Exception as e:
            print("Err:", e)

conn.close()
