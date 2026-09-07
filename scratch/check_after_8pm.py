import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_reminders.sqlite')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]

for table in tables:
    print(f"\n=================== TABLE: {table} ===================")
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [col[1] for col in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM {table}")
    rows = cursor.fetchall()
    print(f"Total rows in {table}: {len(rows)}")
    for r in rows:
        d = dict(r)
        print("  ", d)
