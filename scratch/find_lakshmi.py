import sys
sys.path.insert(0, 'backend')
from database import sqlite_engine
from sqlalchemy import text

with sqlite_engine.connect() as conn:
    rows = conn.execute(text("SELECT sender, group_name, raw_text, timestamp FROM sunfra_raw_messages WHERE lower(raw_text) LIKE '%laksh%' OR lower(sender) LIKE '%laksh%' ORDER BY timestamp DESC")).fetchall()
    print("Found rows:", len(rows))
    for r in rows:
        print(r)
