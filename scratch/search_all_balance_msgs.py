"""
Search for all balance messages in database
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage
from sqlalchemy import desc

db = SessionLocal()
try:
    print("=== SEARCHING RAW MESSAGES FOR BALANCE / CASH / PETTY ===")
    msgs = db.query(RawMessage).filter(
        (RawMessage.raw_text.ilike('%cash%')) | 
        (RawMessage.raw_text.ilike('%bank%')) | 
        (RawMessage.raw_text.ilike('%balance%')) |
        (RawMessage.raw_text.ilike('%petty%'))
    ).order_by(desc(RawMessage.timestamp)).limit(30).all()

    for m in msgs:
        print(f"[{m.timestamp}] Group: {m.group_name} | Sender: {m.sender}")
        print(f"Text: {m.raw_text}")
        print("=" * 60)
finally:
    db.close()
