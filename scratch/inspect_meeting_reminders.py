import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from models import UnifiedReminder

db = SessionLocal()

reminders = db.query(UnifiedReminder).all()
print(f"Total Unified Reminders in DB: {len(reminders)}\n")

for r in reminders:
    if 'meeting' in str(r.report_types or '').lower() or 'meeting' in str(r.task_notes or '').lower() or '120363225998735559' in str(r.whatsapp_group_id):
        print(f"ID: {r.id:3d} | GroupJID: {r.whatsapp_group_id} | Person: {r.person_name} | Status: {r.status} | Trigger: {r.trigger_time}")
        print(f"  Report Types: {r.report_types}")
        print(f"  Task Notes  : {r.task_notes}")
        print("-" * 60)

db.close()
