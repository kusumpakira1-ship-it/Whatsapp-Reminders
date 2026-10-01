import sys
import datetime
from sqlalchemy import text

sys.path.append('backend')
from database import get_db_session

sys.stdout.reconfigure(encoding='utf-8')

today_str = datetime.datetime.now().strftime("%Y-%m-%d")
print(f"================ KUSUM MESSAGES TODAY ({today_str}) ================")

db = get_db_session()
query = text(f"""
    SELECT id, sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE DATE(timestamp) = '{today_str}' 
      AND (LOWER(sender) LIKE '%kusum%' OR sender LIKE '%7259510983%' OR sender LIKE '%7397042004%')
    ORDER BY timestamp ASC
""")

rows = db.execute(query).fetchall()
print(f"Found {len(rows)} total messages sent by Kusum today:\n")

for r in rows:
    msg_id, sender, group_name, raw_text, ts = r
    clean_text = (raw_text or '').replace('\n', ' ')
    print(f"[{ts}] Group: '{group_name}' | Sender: '{sender}'")
    print(f"       Text: \"{clean_text}\"\n")

db.close()
