from database import SessionLocal
from models import RawMessage, WhatsAppMessage

db = SessionLocal()
print("=== Messages sent by Kusum / 7975209680 / Bot Session ===")
raws = db.query(RawMessage).filter(RawMessage.timestamp >= '2026-09-08 00:00:00').all()
for r in raws:
    s = str(r.sender or '')
    txt = str(r.raw_text or '')
    if any(kw in s.lower() for kw in ['kusum', '7975209680', '183300681367688', 'me', 'bot']):
        print(f"RAW: [{r.timestamp.strftime('%H:%M:%S')}] Group: {r.group_name} | Sender: {r.sender} | Text: '{r.raw_text[:60]}'")

w_msgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= '2026-09-08 00:00:00').all()
for w in w_msgs:
    s = str(w.sender_id or '')
    if any(kw in s for kw in ['7975209680', '183300681367688']):
        print(f"W_MSG: [{w.timestamp.strftime('%H:%M:%S')}] Group: {w.group_id} | Sender: {w.sender_id} | Text: '{w.message_text[:60]}'")

# Check if there are any login messages from other senders today in AI & IOT
print("\n=== AI & IOT Group messages today ===")
ai_raws = [r for r in raws if r.group_name and ('ai' in r.group_name.lower() or 'iot' in r.group_name.lower())]
for r in ai_raws:
    print(f"[{r.timestamp.strftime('%H:%M:%S')}] Sender: {r.sender} | Text: '{r.raw_text}'")

db.close()
