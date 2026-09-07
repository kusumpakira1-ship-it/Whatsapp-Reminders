import json
import sqlite3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

print("=== CHECKING waha_groups.json ===")
if os.path.exists('waha_groups.json'):
    with open('waha_groups.json', 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
        for g in data:
            name = g.get('name') or g.get('subject') or ''
            gid = g.get('id') or g.get('jid') or ''
            if any(k in name.lower() for k in ['doc', 'doctor', 'manager', 'manger', 'feedback', 'daily']):
                print(f"  MATCH: '{name}' -> JID: {gid}")

print("\n=== CHECKING SQLITE sunfra_groups ===")
conn = sqlite3.connect('whatsapp_reminders.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()
try:
    c.execute("SELECT * FROM sunfra_groups")
    for r in c.fetchall():
        print(" ", dict(r))
except Exception as e:
    print("Error:", e)

print("\n=== CHECKING MYSQL Group table ===")
try:
    from database import SessionLocal
    from models import Group
    db = SessionLocal()
    grps = db.query(Group).all()
    for g in grps:
        if any(k in (g.name or '').lower() for k in ['doc', 'doctor', 'manager', 'manger', 'feedback']):
            print(f"  MYSQL MATCH: '{g.name}' -> JID: {g.whatsapp_group_id}")
except Exception as e:
    print("MySQL error:", e)
