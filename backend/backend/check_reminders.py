import sys, os
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from dotenv import load_dotenv
load_dotenv(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\.env')

from database import SessionLocal
from models import UnifiedReminder

db = SessionLocal()
reminders = db.query(UnifiedReminder).filter(
    (UnifiedReminder.whatsapp_group_id.like('%hyperscale%')) |
    (UnifiedReminder.whatsapp_group_id.like('%p&l%')) |
    (UnifiedReminder.whatsapp_group_id.like('%120363428417403024%')) |
    (UnifiedReminder.whatsapp_group_id.like('%120363427856964756%'))
).all()

print(f"Found {len(reminders)} reminders:")
for r in reminders:
    print(f"ID: {r.id}")
    print(f"  person_name: {r.person_name}")
    print(f"  person_phone: {r.person_phone}")
    print(f"  whatsapp_group_id: {r.whatsapp_group_id}")
    print(f"  report_types: {r.report_types}")
    print(f"  trigger_time: {r.trigger_time}")
    print(f"  status: {r.status}")
    print("-" * 40)

db.close()
