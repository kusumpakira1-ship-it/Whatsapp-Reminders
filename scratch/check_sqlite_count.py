import sys
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect("whatsapp_reminders.sqlite")
cursor = conn.cursor()

# Check count of sunfra_raw_messages
cursor.execute("SELECT COUNT(*) FROM sunfra_raw_messages;")
print("Count in SQLite sunfra_raw_messages:", cursor.fetchone()[0])

conn.close()
