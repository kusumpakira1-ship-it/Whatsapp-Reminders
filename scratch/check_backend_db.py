import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = 'backend/sunfra_reminders.db'
print("Checking database:", db_path)
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)

for table in ['sunfra_raw_messages', 'sunfra_whatsapp_messages', 'raw_messages', 'whatsapp_messages']:
    if table in tables:
        print(f"\n--- {table} ---")
        cursor.execute(f"SELECT * FROM {table} ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
        print(f"Total rows retrieved: {len(rows)}")
        for r in rows:
            d = dict(r)
            print("  ", d.get('timestamp'), "| GRP:", d.get('group_name') or d.get('group_id'), "| SND:", d.get('sender') or d.get('sender_id'))
            text = str(d.get('raw_text') or d.get('message_text') or '')[:200]
            print("   TEXT:", text.replace('\n', ' '))
