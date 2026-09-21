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

with open(os.path.join(os.path.dirname(__file__), "msgs_out.txt"), "w", encoding="utf-8") as f:
    f.write(f"Total RawMessages today: {len(raws)}\n")
    f.write(f"Total WhatsAppMessages today: {len(was)}\n\n")

    f.write("=== ALL RAW MESSAGES TODAY ===\n")
    for r in raws:
        f.write(f"[{r.timestamp}] Sender: {r.sender} | Group: {r.group_name} | Text: {r.raw_text}\n")

    f.write("\n=== ALL WHATSAPP MESSAGES TODAY ===\n")
    for w in was:
        f.write(f"[{w.timestamp}] Sender: {w.sender_id} | Group: {w.group_id} | Text: {w.message_text}\n")

db.close()
print("Done writing to msgs_out.txt")
