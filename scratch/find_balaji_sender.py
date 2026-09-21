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

with open(os.path.join(os.path.dirname(__file__), "mgmt_group_msgs.txt"), "w", encoding="utf-8") as f:
    f.write("=== ALL MESSAGES IN MANAGEMENT TEAM GROUP TODAY ===\n")
    for r in raws:
        g = str(r.group_name or "").lower()
        if "management" in g or "120363410684018393" in g or "120363406924564250" in g:
            f.write(f"[{r.timestamp}] Sender: {r.sender} | Text: {r.raw_text}\n")

db.close()
print("Done writing mgmt_group_msgs.txt")
