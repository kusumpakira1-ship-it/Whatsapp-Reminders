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

all_msgs.sort(key=lambda x: x['time'])

with open(os.path.join(os.path.dirname(__file__), "all_logins_today.txt"), "w", encoding="utf-8") as f:
    f.write("=== ALL LOGIN / IN MESSAGES TODAY ===\n")
    login_kws = ["login", "in", "good morning", "morning", "present", "sign in"]
    for m in all_msgs:
        t = m['text'].strip().lower()
        if any(kw == t or kw in t.split() for kw in login_kws):
            f.write(f"[{m['time']}] Sender: {m['sender']} | Group: {m['group']} | Text: {m['text']}\n")

db.close()
print("Logins written.")
