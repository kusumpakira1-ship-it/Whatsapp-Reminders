import sys
import datetime
from sqlalchemy import text

sys.path.append('backend')
from database import get_db_session

sys.stdout.reconfigure(encoding='utf-8')

today_str = datetime.datetime.now().strftime("%Y-%m-%d")
db = get_db_session()

query = text(f"""
    SELECT id, sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '{today_str} 10:00:00' AND timestamp <= '{today_str} 10:25:00'
    ORDER BY timestamp ASC
""")
rows = db.execute(query).fetchall()
print(f"Found {len(rows)} messages between 10:00 AM and 10:25 AM:\n")
for r in rows:
    print(f"[{r[4]}] Group: '{r[2]}' | Sender: '{r[1]}' | Text: \"{(r[3] or '').replace('\n', ' ')}\"")

db.close()
