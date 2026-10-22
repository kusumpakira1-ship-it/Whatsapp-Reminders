import sqlite3
import os

db_path = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\whatsapp_reminders.sqlite'
con = sqlite3.connect(db_path)
cur = con.cursor()
try:
    print("Trying REINDEX...")
    cur.execute("REINDEX")
    print("REINDEX done!")
    cur.execute("PRAGMA integrity_check")
    res = cur.fetchall()
    print("Integrity check after REINDEX:", res[:5])
except Exception as e:
    print("REINDEX failed:", e)
con.close()
