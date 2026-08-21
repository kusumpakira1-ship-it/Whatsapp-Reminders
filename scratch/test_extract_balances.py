"""
Test enhanced extract_physical_balances_from_whatsapp
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import re
from datetime import datetime, timezone, timedelta
from database import SessionLocal
from models import RawMessage, WhatsAppMessage, Group
from sqlalchemy import desc, or_

IST = timezone(timedelta(hours=5, minutes=30))

def extract_physical_balances(group_keyword: str):
    db = SessionLocal()
    res = {'petty_cash': None, 'bank_balance': None}
    try:
        # Find group JIDs matching group_keyword
        group_rows = db.query(Group).all()
        target_jids = set()
        for g in group_rows:
            gname = (g.name or '').lower()
            gjid = (g.whatsapp_group_id or '').replace('@g.us', '').lower()
            if group_keyword.lower() in gname:
                target_jids.add(gjid)
                target_jids.add(g.whatsapp_group_id.lower())

        # Also search group_keyword directly
        kw_pattern = f"%{group_keyword}%"
        
        # Query RawMessage
        raw_msgs = db.query(RawMessage).filter(
            or_(
                RawMessage.group_name.ilike(kw_pattern),
                RawMessage.group_name.in_(list(target_jids))
            )
        ).order_by(desc(RawMessage.timestamp)).limit(20).all()

        # Query WhatsAppMessage
        wa_msgs = db.query(WhatsAppMessage).filter(
            or_(
                WhatsAppMessage.group_id.ilike(kw_pattern),
                WhatsAppMessage.group_id.in_(list(target_jids))
            )
        ).order_by(desc(WhatsAppMessage.timestamp)).limit(20).all()

        combined = []
        for m in raw_msgs:
            combined.append({'text': (m.raw_text or '').lower(), 'ts': m.timestamp})
        for m in wa_msgs:
            combined.append({'text': (m.message_text or '').lower(), 'ts': m.timestamp})

        combined.sort(key=lambda x: x['ts'], reverse=True)

        for m in combined:
            text = m['text']

            # Extract Petty Cash / Cash in hand
            if res['petty_cash'] is None:
                p_match = re.search(r'(?:petty\s*cash|cash\s*in\s*hand|closing\s*cash|day\s*book)[^\d]*([\d,]+(?:\.\d+)?)', text)
                if p_match:
                    try:
                        res['petty_cash'] = float(p_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            # Extract Bank Balance
            if res['bank_balance'] is None:
                b_match = re.search(r'(?:bank\s*balance|available\s*bank|bank|indian\s*bank)[^\d]*([\d,]+(?:\.\d+)?)', text)
                if b_match:
                    try:
                        res['bank_balance'] = float(b_match.group(1).replace(',', ''))
                    except ValueError:
                        pass

            if res['petty_cash'] is not None and res['bank_balance'] is not None:
                break
    finally:
        db.close()
    return res

print("=== FEEDS PHYSICAL BALANCES ===")
print(extract_physical_balances('feeds'))

print("=== FARMS PHYSICAL BALANCES ===")
print(extract_physical_balances('poultry'))

print("=== CORPORATE PHYSICAL BALANCES ===")
print(extract_physical_balances('corporate'))
