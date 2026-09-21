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

senders = set()
groups = set()
for r in raws:
    if r.sender:
        senders.add(r.sender)
    if r.group_name:
        groups.add(r.group_name)

with open(os.path.join(os.path.dirname(__file__), "all_senders_out.txt"), "w", encoding="utf-8") as f:
    f.write("=== UNIQUE SENDERS TODAY ===\n")
    for s in sorted(senders):
        f.write(f"- {s}\n")
    
    f.write("\n=== UNIQUE GROUPS TODAY ===\n")
    for g in sorted(groups):
        f.write(f"- {g}\n")

db.close()
print("Senders list written.")
