import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage

db = SessionLocal()
print("=== CHECKING ALL MESSAGES IN 'Sunfra Corporate P&L' GROUP ON 2026-09-03 ===")

raw_msgs = db.query(RawMessage).filter(
    RawMessage.timestamp.like('2026-09-03%')
).all()

corp_raw = [m for m in raw_msgs if 'corporate' in (m.group_name or '').lower()]
print(f"Total Corporate Raw Messages on 03 Sep 2026: {len(corp_raw)}")
for m in corp_raw:
    print(f"[{m.timestamp}] SND: {m.sender}")
    print("TEXT:\n", m.raw_text)
    print("=" * 60)

wa_msgs = db.query(WhatsAppMessage).filter(
    WhatsAppMessage.timestamp.like('2026-09-03%')
).all()

corp_wa = [m for m in wa_msgs if '120363425581380088' in (m.group_id or '').lower()]
print(f"\nTotal Corporate WhatsApp Messages on 03 Sep 2026: {len(corp_wa)}")
for m in corp_wa:
    print(f"[{m.timestamp}] SND_ID: {m.sender_id}")
    print("TEXT:\n", m.message_text)
    print("=" * 60)
