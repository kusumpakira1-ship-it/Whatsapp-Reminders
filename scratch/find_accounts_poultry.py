import sys

sys.path.append('backend')
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

print("================ SEARCHING FOR 'Active Account Balances' OR '1,56,501' IN DB ================")

query = text("""
    SELECT id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE raw_text LIKE '%Active Account Balances%' OR raw_text LIKE '%1,56,501%' OR raw_text LIKE '%11,28,661%' OR raw_text LIKE '%Petty Cash%'
    ORDER BY id DESC
    LIMIT 20
""")

result = db.execute(query)
rows = result.fetchall()

print(f"Total matching rows found: {len(rows)}\n")

for r in rows:
    m_id, g_name, sender, text_c, ts = r
    clean = (text_c or '').replace('\n', ' | ')
    print(f"[{ts}] ID: {m_id} | Group: [{g_name}] | Sender: {sender}")
    print(f"    Text: {clean}\n" + "-"*60)

db.close()
