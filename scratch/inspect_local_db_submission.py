"""
Inspect database tables, particularly for report logs, submissions, sub-reports, and reminders for 2026-08-13.
"""
import sqlite3, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Let's check local database or Hostinger DB scripts
db_path = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\whatsapp_reminders.sqlite'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in c.fetchall()]
    print("Local SQLite Tables:", tables)
    
    for t in tables:
        try:
            c.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = c.fetchone()[0]
            print(f"  {t}: {cnt} rows")
        except Exception as e:
            print(f"  {t}: {e}")

