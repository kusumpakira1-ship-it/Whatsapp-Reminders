import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_reminders.sqlite')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT group_name, sender, raw_text, timestamp FROM sunfra_raw_messages WHERE timestamp LIKE '2026-09-03%' ORDER BY timestamp DESC")
rows = cursor.fetchall()
print(f"Total raw messages on 2026-09-03: {len(rows)}")
for r in rows[:15]:
    print("GRP:", r['group_name'], "| SND:", r['sender'], "| TS:", r['timestamp'])
    print("TEXT:", (r['raw_text'] or '')[:150])
    print("-" * 50)

cursor.execute("SELECT group_id, sender_id, message_text, timestamp FROM sunfra_whatsapp_messages WHERE timestamp LIKE '2026-09-03%' ORDER BY timestamp DESC")
rows2 = cursor.fetchall()
print(f"\nTotal whatsapp messages on 2026-09-03: {len(rows2)}")
for r in rows2[:15]:
    print("GRP_ID:", r['group_id'], "| SND_ID:", r['sender_id'], "| TS:", r['timestamp'])
    print("TEXT:", (r['message_text'] or '')[:150])
    print("-" * 50)
