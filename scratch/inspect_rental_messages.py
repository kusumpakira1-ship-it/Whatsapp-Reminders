import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from database import SessionLocal
from models import RawMessage, ProcessedData, WhatsAppMessage

db = SessionLocal()
group_jid = "120363409299826962@g.us"

raws = db.query(RawMessage).filter(RawMessage.group_name.like("%Rental%")).order_by(RawMessage.timestamp.desc()).limit(20).all()
print(f"=== RAW MESSAGES FROM RENTAL UPDATES ({len(raws)} found) ===")
for r in raws:
    print(f"[{r.timestamp}] Sender: {r.sender} | Msg: {r.raw_text}")

wmsgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.group_id.like("%120363409299826962%")).order_by(WhatsAppMessage.timestamp.desc()).limit(20).all()
print(f"\n=== WHATSAPP MESSAGES FROM RENTAL UPDATES ({len(wmsgs)} found) ===")
for w in wmsgs:
    print(f"[{w.timestamp}] Sender: {w.sender_id} | Content: {w.message_text}")

db.close()
