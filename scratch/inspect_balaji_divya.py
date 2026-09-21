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

with open(os.path.join(os.path.dirname(__file__), "bd_out.txt"), "w", encoding="utf-8") as f:
    f.write("=== SEARCH FOR BALAJI IN ALL MESSAGES & SENDERS TODAY ===\n")
    balaji_aliases = ["balaji", "reddy", "9493928388", "242695733772318"]
    for m in all_msgs:
        s_low = m['sender'].lower()
        t_low = m['text'].lower()
        if any(al in s_low or al in t_low for al in balaji_aliases):
            f.write(f"[{m['time']}] [{m['source']}] Sender: {m['sender']} | Group: {m['group']} | Text: {m['text']}\n")

    f.write("\n=== SEARCH FOR DIVYA IN ALL MESSAGES & SENDERS TODAY ===\n")
    divya_aliases = ["divya", "56556230058144", "9381255565", "😐"]
    for m in all_msgs:
        s_low = m['sender'].lower()
        t_low = m['text'].lower()
        if any(al in s_low or al in t_low for al in divya_aliases):
            f.write(f"[{m['time']}] [{m['source']}] Sender: {m['sender']} | Group: {m['group']} | Text: {m['text']}\n")

db.close()
print("BD inspection done.")
