import sys

sys.path.append('backend')
from database import SessionLocal
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = SessionLocal()

print("================ TODAY'S UNIQUE SENDERS ================")
rows = db.execute(text("SELECT DISTINCT sender, group_name FROM sunfra_raw_messages WHERE timestamp >= '2026-09-17 00:00:00'")).fetchall()
for r in rows:
    print(f"Sender: '{r[0]}' | Group: '{r[1]}'")

db.close()
