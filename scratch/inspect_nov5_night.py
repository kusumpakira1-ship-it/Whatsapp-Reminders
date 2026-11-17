import sys
sys.path.insert(0, 'backend')
from database import get_db_session
from sqlalchemy import text

db = get_db_session()

print("=== 1. sunfra_whatsapp_messages ===")
rows = db.execute(text("SELECT id, group_id, sender_phone, LEFT(message_text, 60), timestamp FROM sunfra_whatsapp_messages WHERE timestamp >= '2026-11-05 23:40:00' ORDER BY timestamp ASC")).fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(r)

print("\n=== 2. sunfra_raw_messages ===")
rows = db.execute(text("SELECT id, group_name, sender, LEFT(raw_text, 60), timestamp FROM sunfra_raw_messages WHERE timestamp >= '2026-11-05 23:40:00' ORDER BY timestamp ASC")).fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(r)

print("\n=== 3. sunfra_water_alerts ===")
rows = db.execute(text("SELECT * FROM sunfra_water_alerts WHERE created_at >= '2026-11-05 23:00:00' ORDER BY created_at ASC")).fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(r)

print("\n=== 4. sunfra_reminder_logs ===")
rows = db.execute(text("SELECT * FROM sunfra_reminder_logs WHERE created_at >= '2026-11-05 23:00:00' ORDER BY created_at ASC")).fetchall()
print(f"Total rows: {len(rows)}")
for r in rows:
    print(r)
