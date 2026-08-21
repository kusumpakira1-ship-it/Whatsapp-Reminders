"""
Inspect all reminders in DB
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import UnifiedReminder, Group

db = SessionLocal()
rems = db.query(UnifiedReminder).all()
for r in rems:
    grp_name = ""
    if r.whatsapp_group_id:
        g = db.query(Group).filter(Group.whatsapp_group_id == r.whatsapp_group_id).first()
        if g: grp_name = g.name
    print(f"ID: {r.id} | Name: '{r.person_name}' | GroupID: '{r.whatsapp_group_id}' (Name: '{grp_name}') | Reports: '{r.report_types}'")

db.close()
