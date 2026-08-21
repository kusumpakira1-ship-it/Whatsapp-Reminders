"""
Inspect sunfra_groups table
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import Group

db = SessionLocal()
try:
    groups = db.query(Group).all()
    print("=== SUNFRA GROUPS IN DATABASE ===")
    for g in groups:
        print(f"ID: {g.id} | Name: '{g.name}' | JID: '{g.whatsapp_group_id}'")
finally:
    db.close()
