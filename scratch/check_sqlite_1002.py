import sqlite3
import datetime

today_str = datetime.datetime.now().strftime("%Y-%m-%d")
conn = sqlite3.connect("whatsapp_reminders.sqlite")
cursor = conn.cursor()

cursor.execute(f"""
    SELECT id, sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '{today_str} 09:55:00' AND timestamp <= '{today_str} 10:15:00'
    ORDER BY timestamp ASC
""")
rows = cursor.fetchall()
print(f"Found {len(rows)} messages in local SQLite fallback between 09:55 and 10:15:\n")
for r in rows:
    print(f"[{r[4]}] Group: '{r[2]}' | Sender: '{r[1]}' | Text: \"{(r[3] or '').replace('\n', ' ')}\"")

conn.close()
