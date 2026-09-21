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

aliases = ["lakshmi", "lakshmy", "137812783452345"]

with open(os.path.join(os.path.dirname(__file__), "lakshmi_out.txt"), "w", encoding="utf-8") as f:
    f.write("=== RAW MESSAGES MATCHING LAKSHMI ===\n")
    for r in raws:
        s_str = str(r.sender or "").lower()
        t_str = str(r.raw_text or "").lower()
        if any(al in s_str or al in t_str for al in aliases):
            f.write(f"[{r.timestamp}] Sender: {r.sender} | Group: {r.group_name} | Text: {r.raw_text}\n")
            
    f.write("\n=== WA MESSAGES MATCHING LAKSHMI ===\n")
    for w in was:
        s_str = str(w.sender_id or "").lower()
        t_str = str(w.message_text or "").lower()
        if any(al in s_str or al in t_str for al in aliases):
            f.write(f"[{w.timestamp}] Sender: {w.sender_id} | Group: {w.group_id} | Text: {w.message_text}\n")

db.close()
print("Lakshmi inspection done.")
