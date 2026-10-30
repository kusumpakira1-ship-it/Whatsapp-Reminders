import sys
import os
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append('backend')
from database import get_db_session
from models import RawMessage, WhatsAppMessage

db = get_db_session()

start_dt = datetime(2026, 10, 28, 0, 0, 0)
end_dt = datetime(2026, 10, 29, 13, 0, 0)

print(f"=== CHECKING ALL MESSAGES ON 28 OCT BY ACCOUNTANTS / KEYWORDS ===")

# Check distinct senders and groups on 28 Oct
raw_senders = db.query(RawMessage.sender, RawMessage.group_name).filter(RawMessage.timestamp >= start_dt, RawMessage.timestamp <= end_dt).distinct().all()
print("\nActive senders & groups on 28 Oct (RawMessage):")
for s, g in set(raw_senders):
    print(f"- Sender: '{s}' | Group: '{g}'")

# Search for any message containing sales, purchase, payable, receivable, daybook, etc.
keywords = ['sale', 'purchase', 'payable', 'receivable', 'day book', 'daybook', 'balance', 'p&l', 'silo']
found_msgs = []
all_raw = db.query(RawMessage).filter(RawMessage.timestamp >= start_dt, RawMessage.timestamp <= end_dt).all()
for m in all_raw:
    txt = (m.raw_text or '').lower()
    for kw in keywords:
        if kw in txt:
            found_msgs.append(m)
            break

print(f"\nTotal RawMessages matching accounting keywords: {len(found_msgs)}")
for m in found_msgs:
    print(f"[{m.timestamp}] Grp: '{m.group_name}' | Sender: '{m.sender}' | Type: {m.message_type}")
    print(f"Text: {repr(m.raw_text)}")
    print("-" * 50)

db.close()
