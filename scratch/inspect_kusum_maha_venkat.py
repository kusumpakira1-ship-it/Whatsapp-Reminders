import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from models import RawMessage, WhatsAppMessage

db = get_db_session()

target_date = "2026-09-19"

raws = db.query(RawMessage).filter(
    RawMessage.timestamp >= f"{target_date} 00:00:00",
    RawMessage.timestamp <= f"{target_date} 23:59:59"
).all()

was = db.query(WhatsAppMessage).filter(
    WhatsAppMessage.timestamp >= f"{target_date} 00:00:00",
    WhatsAppMessage.timestamp <= f"{target_date} 23:59:59"
).all()

all_msgs = []
for r in raws:
    all_msgs.append({
        'time': r.timestamp,
        'sender': str(r.sender or ''),
        'group': str(r.group_name or ''),
        'text': str(r.raw_text or ''),
        'source': 'RawMessage'
    })
for w in was:
    all_msgs.append({
        'time': w.timestamp,
        'sender': str(w.sender_id or ''),
        'group': str(w.group_id or ''),
        'text': str(w.message_text or ''),
        'source': 'WhatsAppMessage'
    })

all_msgs.sort(key=lambda x: x['time'])

queries = {
    'Kusum': ['kusum', '7975209680', '183300681367688', '7259510983'],
    'Mahalakshmi': ['mahalakshmi', '6364817749', '184791135711366'],
    'Venkat': ['venkat', '8247586860', '45586833240126']
}

with open(os.path.join(os.path.dirname(__file__), "kmv_out.txt"), "w", encoding="utf-8") as f:
    for name, aliases in queries.items():
        f.write(f"\n==================== {name.upper()} ====================\n")
        matched = []
        for m in all_msgs:
            s_low = m['sender'].lower()
            t_low = m['text'].lower()
            if any(al.lower() in s_low or al.lower() in t_low for al in aliases):
                matched.append(m)
        f.write(f"Total matching messages: {len(matched)}\n")
        for m in matched:
            f.write(f"[{m['time']}] [{m['source']}] Sender: {m['sender']} | Group: {m['group']} | Text: {m['text']}\n")

db.close()
print("KMV inspection complete.")
