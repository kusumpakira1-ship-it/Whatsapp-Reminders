import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage

try:
    db = SessionLocal()
    print("Connected to MySQL successfully!")
    
    # Query raw messages on 2026-09-03
    raw_msgs = db.query(RawMessage).filter(RawMessage.timestamp.like('2026-09-03%')).all()
    print(f"Total MySQL Raw Messages on 2026-09-03: {len(raw_msgs)}")
    for m in raw_msgs:
        print(f"[{m.timestamp}] GRP: {m.group_name} | SND: {m.sender}")
        print("  TEXT:", (m.raw_text or '')[:300].replace('\n', ' '))
        print("-" * 60)
        
    wa_msgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp.like('2026-09-03%')).all()
    print(f"\nTotal MySQL WhatsApp Messages on 2026-09-03: {len(wa_msgs)}")
    for m in wa_msgs:
        print(f"[{m.timestamp}] GRP_ID: {m.group_id} | SND_ID: {m.sender_id}")
        print("  TEXT:", (m.message_text or '')[:300].replace('\n', ' '))
        print("-" * 60)

except Exception as e:
    print("MySQL query failed:", e)
