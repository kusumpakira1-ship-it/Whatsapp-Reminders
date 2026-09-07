import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

print("=== ALL WAHA GROUPS ===")
if os.path.exists('waha_groups.json'):
    with open('waha_groups.json', 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
        for idx, g in enumerate(data):
            name = g.get('name') or g.get('subject') or ''
            gid = g.get('id') or g.get('jid') or ''
            print(f"{idx+1}. Name: '{name}' | ID: {gid}")

print("\n=== ALL MYSQL GROUPS ===")
try:
    from database import SessionLocal
    from models import Group
    db = SessionLocal()
    grps = db.query(Group).all()
    for idx, g in enumerate(grps):
        print(f"{idx+1}. Name: '{g.name}' | JID: {g.whatsapp_group_id}")
except Exception as e:
    print("Error:", e)
