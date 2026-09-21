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

with open(os.path.join(os.path.dirname(__file__), "deep_search_out.txt"), "w", encoding="utf-8") as f:
    f.write("=== 1. SEARCH FOR ASIF / SUNFRA OLX CEE GROUP MESSAGES ===\n")
    for m in all_msgs:
        g = m['group'].lower()
        s = m['sender'].lower()
        t = m['text'].lower()
        if 'olx' in g or 'cee' in g or '120363428895707621' in g or 'asif' in s or '6364063475' in s or 'asif' in t:
            f.write(f"[{m['time']}] Sender: {m['sender']} | Group: {m['group']} | Text: {m['text']}\n")

    f.write("\n=== 2. SEARCH FOR BALAJI / MANAGEMENT TEAM / ALL GROUPS MESSAGES ===\n")
    for m in all_msgs:
        g = m['group'].lower()
        s = m['sender'].lower()
        t = m['text'].lower()
        if 'balaji' in s or '9493928388' in s or '242695733772318' in s or 'balaji' in t or 'management' in g:
            f.write(f"[{m['time']}] Sender: {m['sender']} | Group: {m['group']} | Text: {m['text']}\n")

    f.write("\n=== 3. SEARCH FOR ROOPA ALL GROUPS ===\n")
    for m in all_msgs:
        s = m['sender'].lower()
        t = m['text'].lower()
        if 'roopa' in s or 'rupa' in s or '147635256201243' in s or '8686856459' in s:
            f.write(f"[{m['time']}] Sender: {m['sender']} | Group: {m['group']} | Text: {m['text']}\n")

    f.write("\n=== 4. SEARCH FOR JAGADISH ALL GROUPS ===\n")
    for m in all_msgs:
        s = m['sender'].lower()
        t = m['text'].lower()
        if 'jagadish' in s or '7676711899' in s or '217183829389549' in s:
            f.write(f"[{m['time']}] Sender: {m['sender']} | Group: {m['group']} | Text: {m['text']}\n")

db.close()
print("Deep search complete.")
