import sys

sys.path.append('backend')
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

print("================ SEARCHING FOR MAHALAKSHMI MESSAGES ON 16 SEP 2026 ================")

query = text("""
    SELECT id, group_name, sender, raw_text, message_type, media_path, timestamp 
    FROM sunfra_raw_messages 
    WHERE (sender LIKE '%mahalakshmi%' OR sender LIKE '%184791135711366%' OR group_name LIKE '%poultry%' OR group_name LIKE '%accounts%')
      AND timestamp >= '2026-09-16 00:00:00' AND timestamp <= '2026-09-16 23:59:59'
    ORDER BY timestamp ASC
""")
result = db.execute(query)
rows = result.fetchall()

print(f"Total matching messages: {len(rows)}\n")

for r in rows:
    m_id, g_name, sender, text_c, m_type, m_path, ts = r
    clean_text = (text_c or '').replace('\n', ' | ')
    print(f"[{ts}] Group: [{g_name}] | Sender: {sender} | Type: {m_type}")
    print(f"    Text: {clean_text}")
    print(f"    Media: {m_path}\n" + "-"*60)

db.close()
