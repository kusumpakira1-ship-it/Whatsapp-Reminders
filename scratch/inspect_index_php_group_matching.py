"""
Inspect index.php group matching logic for Accounts Poultry and Corporate P&L
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, Group
from sqlalchemy import or_

db = SessionLocal()
try:
    print("=== RAW MESSAGES FOR CORPORATE P&L ===")
    corp_msgs = db.query(RawMessage).filter(
        or_(
            RawMessage.group_name.ilike('%corporate%'),
            RawMessage.group_name.ilike('%120363425581380088%')
        )
    ).all()
    print(f"Found {len(corp_msgs)} raw messages for Corporate P&L.")
    for m in corp_msgs[:10]:
        print(f"[{m.timestamp}] Group: '{m.group_name}' | Text: '{m.raw_text}'")

    print("\n=== RAW MESSAGES FOR ACCOUNTS POULTRY ===")
    poultry_msgs = db.query(RawMessage).filter(
        or_(
            RawMessage.group_name.ilike('%poultry%'),
            RawMessage.group_name.ilike('%120363042907512705%')
        )
    ).all()
    print(f"Found {len(poultry_msgs)} raw messages for Accounts Poultry.")
    for m in poultry_msgs[:10]:
        print(f"[{m.timestamp}] Group: '{m.group_name}' | Text: '{m.raw_text}'")
finally:
    db.close()
