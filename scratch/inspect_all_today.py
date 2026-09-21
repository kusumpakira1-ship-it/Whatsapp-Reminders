import sys

sys.path.append('backend')
from database import SessionLocal
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = SessionLocal()

print("================ ALL MESSAGES RECEIVED TODAY (17 SEP 2026) ================")

query = text("""
    SELECT group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '2026-09-17 00:00:00'
    ORDER BY timestamp ASC
""")

rows = db.execute(query).fetchall()
print(f"Total raw messages received today (17 Sep 2026): {len(rows)}\n")

for r in rows:
    clean_text = (r[2] or '').replace('\n', ' | ')
    print(f"[{r[3]}] Group: [{r[0]}] | Sender: {r[1]}")
    print(f"    Text: {clean_text}\n" + "-"*60)

db.close()
