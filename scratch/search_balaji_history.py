import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from models import RawMessage, WhatsAppMessage

db = get_db_session()

print("Searching historical messages for Balaji...")

raws = db.query(RawMessage).filter(
    (RawMessage.sender.like("%balaji%")) |
    (RawMessage.sender.like("%9493928388%")) |
    (RawMessage.raw_text.like("%balaji%"))
).order_by(RawMessage.timestamp.desc()).limit(20).all()

was = db.query(WhatsAppMessage).filter(
    (WhatsAppMessage.sender_id.like("%balaji%")) |
    (WhatsAppMessage.sender_id.like("%9493928388%")) |
    (WhatsAppMessage.message_text.like("%balaji%"))
).order_by(WhatsAppMessage.timestamp.desc()).limit(20).all()

with open(os.path.join(os.path.dirname(__file__), "balaji_history_out.txt"), "w", encoding="utf-8") as f:
    f.write("=== RAW MESSAGES FOR BALAJI HISTORY ===\n")
    for r in raws:
        f.write(f"[{r.timestamp}] Sender: {r.sender} | Group: {r.group_name} | Text: {r.raw_text}\n")
        
    f.write("\n=== WA MESSAGES FOR BALAJI HISTORY ===\n")
    for w in was:
        f.write(f"[{w.timestamp}] Sender: {w.sender_id} | Group: {w.group_id} | Text: {w.message_text}\n")

db.close()
print("Done writing balaji_history_out.txt")
