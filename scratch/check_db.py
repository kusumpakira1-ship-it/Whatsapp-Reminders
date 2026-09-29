import sqlite3
import json

conn = sqlite3.connect('whatsapp_reminders.sqlite')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

for t in tables:
    print(f"\n--- TABLE: {t} ---")
    cursor.execute(f"PRAGMA table_info('{t}')")
    cols = [col[1] for col in cursor.fetchall()]
    print("Columns:", cols)
    cursor.execute(f"SELECT * FROM '{t}' ORDER BY 1 DESC LIMIT 10")
    rows = cursor.fetchall()
    print(f"Sample rows (up to 10): {len(rows)}")
    for r in rows:
        print(r)
