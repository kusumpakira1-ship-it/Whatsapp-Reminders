import sys

sys.path.append('backend')
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

print("================ ALL MESSAGES RECEIVED ON 16 SEP BETWEEN 19:00 AND 20:00 ================")

query = text("""
    SELECT id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '2026-09-16 19:00:00' AND timestamp <= '2026-09-16 20:00:00'
    ORDER BY timestamp ASC
""")
res = db.execute(query)
rows = res.fetchall()

print(f"Total raw messages received in 19:00 - 20:00 window: {len(rows)}\n")

for r in rows:
    m_id, g_name, sender, text_c, ts = r
    clean = (text_c or '').replace('\n', ' | ')
    print(f"[{ts}] ID: {m_id} | Group: [{g_name}] | Sender: {sender}")
    print(f"    Text: {clean}\n" + "-"*60)

db.close()
