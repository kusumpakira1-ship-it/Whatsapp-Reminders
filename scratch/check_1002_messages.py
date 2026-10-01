import sys
import datetime
from sqlalchemy import text

sys.path.append('backend')
from database import get_db_session

sys.stdout.reconfigure(encoding='utf-8')

today_str = datetime.datetime.now().strftime("%Y-%m-%d")
print(f"================ MESSAGES AROUND 10:00 AM - 10:05 AM TODAY ({today_str}) ================")

db = get_db_session()

# Query sunfra_raw_messages
query1 = text(f"""
    SELECT id, sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= '{today_str} 09:55:00' AND timestamp <= '{today_str} 10:10:00'
    ORDER BY timestamp ASC
""")
rows1 = db.execute(query1).fetchall()
print(f"Found {len(rows1)} messages in sunfra_raw_messages between 09:55 and 10:10:\n")
for r in rows1:
    print(f"[{r[4]}] Group: '{r[2]}' | Sender: '{r[1]}' | Text: \"{(r[3] or '').replace('\n', ' ')}\"")

print("\n------------------------------------------------------------\n")

# Query whatsapp_messages table if exists
try:
    query2 = text(f"""
        SELECT message_id, sender_phone, group_id, message_body, timestamp 
        FROM whatsapp_messages 
        WHERE timestamp >= '{today_str} 09:55:00' AND timestamp <= '{today_str} 10:10:00'
        ORDER BY timestamp ASC
    """)
    rows2 = db.execute(query2).fetchall()
    print(f"Found {len(rows2)} messages in whatsapp_messages between 09:55 and 10:10:\n")
    for r in rows2:
        print(f"[{r[4]}] Group: '{r[2]}' | Sender: '{r[1]}' | Text: \"{(r[3] or '').replace('\n', ' ')}\"")
except Exception as e:
    print("whatsapp_messages table query error:", e)

db.close()
