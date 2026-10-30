import json
import sys
import os
sys.path.append('backend')
from database import get_db_session
from models import RawMessage, WhatsAppMessage

sys.stdout.reconfigure(encoding='utf-8')

print("=== SEARCHING WAHA GROUPS JSON ===")
if os.path.exists('waha_groups.json'):
    with open('waha_groups.json', 'r', encoding='utf-8') as f:
        groups = json.load(f)
    for g in groups:
        name = g.get('name', '')
        if 'raj' in name.lower():
            print(f"waha_groups: ID={g.get('id')} | Name='{name}'")

print("\n=== SEARCHING DATABASE FOR RAJ GROUPS / MESSAGES ===")
db = get_db_session()
try:
    from sqlalchemy import or_
    raws = db.query(RawMessage.group_name).filter(RawMessage.group_name.ilike('%raj%')).distinct().all()
    print("Distinct RawMessage groups:", [r[0] for r in raws])
    
    was = db.query(WhatsAppMessage.group_id).filter(WhatsAppMessage.group_id.ilike('%raj%')).distinct().all()
    print("Distinct WhatsAppMessage group_ids:", [w[0] for w in was])
    
    # Also check recent messages mentioning 'raj'
    msgs = db.query(RawMessage).filter(RawMessage.group_name.ilike('%raj%')).order_by(RawMessage.timestamp.desc()).limit(5).all()
    print(f"\nRecent RawMessages from Raj groups: {len(msgs)}")
    for m in msgs:
        print(f"[{m.timestamp}] Group='{m.group_name}' | Text:\n{m.raw_text}\n---")
finally:
    db.close()
