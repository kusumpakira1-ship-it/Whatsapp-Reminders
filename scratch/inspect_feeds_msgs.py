"""
Inspect recent WhatsApp messages for Feeds, Farms, and Corporate groups
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage
from sqlalchemy import desc

db = SessionLocal()
try:
    print("=== RAW MESSAGES FOR FEEDS GROUP ===")
    raw_feeds = db.query(RawMessage).filter(RawMessage.group_name.ilike('%feed%')).order_by(desc(RawMessage.timestamp)).limit(10).all()
    for m in raw_feeds:
        print(f"[{m.timestamp}] Sender: {m.sender} | Group: {m.group_name}")
        print(f"Text: {m.raw_text[:300]}")
        print("-" * 50)

    print("\n=== WHATSAPP MESSAGES FOR FEEDS GROUP ===")
    wa_feeds = db.query(WhatsAppMessage).filter(WhatsAppMessage.group_id.ilike('%feed%')).order_by(desc(WhatsAppMessage.timestamp)).limit(10).all()
    for m in wa_feeds:
        print(f"[{m.timestamp}] Sender: {m.sender_id} | Group: {m.group_id}")
        print(f"Text: {(m.message_text or '')[:300]}")
        print("-" * 50)
finally:
    db.close()
