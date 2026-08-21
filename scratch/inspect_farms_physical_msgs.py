"""
Inspect recent WhatsApp messages from Accounts Poultry and Payments - Sunfra Farms
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage, Group
from sqlalchemy import desc, or_

db = SessionLocal()
try:
    print("=== RAW MESSAGES FOR POULTRY / FARMS ===")
    msgs = db.query(RawMessage).filter(
        or_(
            RawMessage.group_name.ilike('%poultry%'),
            RawMessage.group_name.ilike('%farms%'),
            RawMessage.group_name.ilike('%accounts%')
        )
    ).order_by(desc(RawMessage.timestamp)).limit(30).all()

    for m in msgs:
        print(f"[{m.timestamp}] Group: {m.group_name} | Sender: {m.sender}")
        print(f"Text: {m.raw_text[:400]}")
        print("=" * 60)
finally:
    db.close()
