"""
Inspect Raw Material reminder fields
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import UnifiedReminder

db = SessionLocal()
rems = db.query(UnifiedReminder).filter(UnifiedReminder.person_name.ilike('%raw material%')).all()
for r in rems:
    print(f"ID: {r.id} | Name: '{r.person_name}' | GroupID: '{r.whatsapp_group_id}' | Reports: '{r.report_types}'")

db.close()
