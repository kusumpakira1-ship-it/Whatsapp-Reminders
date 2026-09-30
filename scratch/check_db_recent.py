import sqlite3
import os
import json
from datetime import datetime

db_path = os.path.join("backend", "whatsapp_reminders.sqlite")
print(f"Checking DB: {db_path} (exists: {os.path.exists(db_path)})")

if not os.path.exists(db_path):
    db_path = "whatsapp_reminders.sqlite"
    print(f"Fallback to root DB: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in DB:", tables)

for table in tables:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"\n--- Table: {table} (Columns: {cols}) ---")
    
    # Check max timestamp or date column
    date_cols = [c for c in cols if 'time' in c.lower() or 'date' in c.lower() or 'created' in c.lower() or 'at' in c.lower()]
    
    cursor.execute(f"SELECT count(*) FROM {table}")
    total_count = cursor.fetchone()[0]
    print(f"Total rows: {total_count}")
    
    if date_cols:
        for dcol in date_cols:
            try:
                cursor.execute(f"SELECT MIN({dcol}), MAX({dcol}) FROM {table}")
                min_t, max_t = cursor.fetchone()
                print(f"  Col [{dcol}] -> Min: {min_t}, Max: {max_t}")
                
                # Query records between 2026-09-28 08:00:00 and 2026-09-29 10:30:00
                cursor.execute(f"SELECT count(*) FROM {table} WHERE {dcol} >= '2026-09-28 08:00:00' AND {dcol} <= '2026-09-29 10:30:00'")
                recent_count = cursor.fetchone()[0]
                print(f"  Col [{dcol}] -> Rows between 2026-09-28 08:00 and today 10:30: {recent_count}")
            except Exception as e:
                print(f"  Col [{dcol}] query error: {e}")

conn.close()
