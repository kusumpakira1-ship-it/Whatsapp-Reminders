import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage

db = SessionLocal()
print("Searching MySQL for balance messages on 2026-09-03...")

keywords = ['bank', 'cash', 'petty', 'undeposited', 'indian', 'sbi', 'od', 'closing', 'balance', 'bal']

raw_msgs = db.query(RawMessage).filter(RawMessage.timestamp.like('2026-09-03%')).all()
matching_raw = []
for m in raw_msgs:
    txt = (m.raw_text or '').lower()
    if any(k in txt for k in keywords):
        matching_raw.append(m)

print(f"Matching Raw Messages: {len(matching_raw)}")
for m in matching_raw:
    print(f"[{m.timestamp}] GRP: '{m.group_name}' | SND: '{m.sender}'")
    print("  TEXT:", m.raw_text)
    print("=" * 60)

wa_msgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp.like('2026-09-03%')).all()
matching_wa = []
for m in wa_msgs:
    txt = (m.message_text or '').lower()
    if any(k in txt for k in keywords):
        matching_wa.append(m)

print(f"\nMatching WhatsApp Messages: {len(matching_wa)}")
for m in matching_wa:
    print(f"[{m.timestamp}] GRP_ID: '{m.group_id}' | SND_ID: '{m.sender_id}'")
    print("  TEXT:", m.message_text)
    print("=" * 60)
