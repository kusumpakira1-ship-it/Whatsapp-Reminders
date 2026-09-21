import sys

sys.path.append('backend')
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

print("================ CHECKING MAHALAKSHMI'S 19:51:53 MESSAGE ================")
query = text("""
    SELECT id, group_name, sender, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE (sender LIKE '%mahalakshmi%' OR sender LIKE '%184791135711366%') AND date(timestamp) = '2026-09-16'
    ORDER BY timestamp ASC
""")
rows = db.execute(query).fetchall()

for r in rows:
    print(f"[{r[4]}] Group: [{r[1]}] | Sender: {r[2]} | Text: '{r[3]}'")

db.close()
