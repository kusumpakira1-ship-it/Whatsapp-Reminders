import sys
import sqlite3
import os

sys.stdout.reconfigure(encoding='utf-8')

db_file = "whatsapp_reminders.sqlite"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

print("================ CHECKING SQLITE FOR 16 SEP MESSAGES ================")
cursor.execute("SELECT COUNT(*) FROM sunfra_raw_messages WHERE date(timestamp) = '2026-09-16';")
cnt_16 = cursor.fetchone()[0]
print(f"Total 16 Sep messages in SQLite: {cnt_16}")

cursor.execute("SELECT COUNT(*) FROM sunfra_raw_messages WHERE date(timestamp) = '2026-09-17';")
cnt_17 = cursor.fetchone()[0]
print(f"Total 17 Sep messages in SQLite: {cnt_17}")

conn.close()
