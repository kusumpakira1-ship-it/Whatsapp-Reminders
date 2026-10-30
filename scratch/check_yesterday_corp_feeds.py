import sys
import os
from datetime import datetime, timedelta
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append('backend')
from database import get_db_session
from models import RawMessage, WhatsAppMessage

db = get_db_session()

start_dt = datetime(2026, 10, 28, 0, 0, 0)
end_dt = datetime(2026, 10, 29, 13, 0, 0)

print(f"=== CHECKING MESSAGES FROM {start_dt} TO {end_dt} ===")

raw_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= start_dt, RawMessage.timestamp <= end_dt).order_by(RawMessage.timestamp.asc()).all()
wa_msgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= start_dt, WhatsAppMessage.timestamp <= end_dt).order_by(WhatsAppMessage.timestamp.asc()).all()

print(f"Total RawMessages: {len(raw_msgs)}")
print(f"Total WhatsAppMessages: {len(wa_msgs)}")

print("\n--- CORPORATE RELATED MESSAGES ---")
for m in raw_msgs:
    grp = (m.group_name or '').lower()
    txt = (m.raw_text or '')
    if any(k in grp for k in ['corp', 'corporate', 'sunfra corporate']):
        print(f"[{m.timestamp}] (Raw) Grp: '{m.group_name}' | Sender: {m.sender} | Type: {m.message_type}")
        print(f"Text snippet: {txt[:300]}")
        print("-" * 40)

for m in wa_msgs:
    grp = (m.group_id or '').lower()
    txt = (m.message_text or '')
    if any(k in grp for k in ['corp', 'corporate', 'sunfra corporate', '120363425581380088']):
        print(f"[{m.timestamp}] (WA) Grp: '{m.group_id}' | Sender: {m.sender_id}")
        print(f"Text snippet: {txt[:300]}")
        print("-" * 40)

print("\n--- FEEDS RELATED MESSAGES ---")
for m in raw_msgs:
    grp = (m.group_name or '').lower()
    txt = (m.raw_text or '')
    if any(k in grp for k in ['feed', 'feeds', 'sunfra feed']):
        print(f"[{m.timestamp}] (Raw) Grp: '{m.group_name}' | Sender: {m.sender} | Type: {m.message_type}")
        print(f"Text snippet: {txt[:300]}")
        print("-" * 40)

for m in wa_msgs:
    grp = (m.group_id or '').lower()
    txt = (m.message_text or '')
    if any(k in grp for k in ['feed', 'feeds', 'sunfra feed', '120363428748481277']):
        print(f"[{m.timestamp}] (WA) Grp: '{m.group_id}' | Sender: {m.sender_id}")
        print(f"Text snippet: {txt[:300]}")
        print("-" * 40)

db.close()
