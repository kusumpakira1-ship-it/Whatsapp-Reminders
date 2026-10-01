import sys
import datetime
from sqlalchemy import text

sys.path.append('backend')
from database import get_db_session

sys.stdout.reconfigure(encoding='utf-8')

today_str = datetime.datetime.now().strftime("%Y-%m-%d")
db = get_db_session()

# Search raw_text, sender, or group_name for '10:02' or 'kusum' or 'login'
query = text(f"""
    SELECT id, sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE DATE(timestamp) = '{today_str}' 
      AND (
          timestamp BETWEEN '{today_str} 10:00:00' AND '{today_str} 10:05:00'
          OR LOWER(sender) LIKE '%kusum%'
          OR LOWER(sender) LIKE '%7259510983%'
          OR LOWER(sender) LIKE '%7975209680%'
      )
    ORDER BY timestamp ASC
""")

rows = db.execute(query).fetchall()
print(f"Total matching rows found: {len(rows)}\n")

for r in rows:
    msg_id, sender, group_name, raw_text, ts = r
    clean_text = (raw_text or '').replace('\n', ' ')
    print(f"[{ts}] Group: '{group_name}' | Sender: '{sender}' | Text: \"{clean_text[:80]}\"")

db.close()
