import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from waha_service import send_waha_message
from database import SessionLocal
from models import UnifiedReminder
from scheduler import build_reminder_body

db = SessionLocal()
r = db.query(UnifiedReminder).filter(UnifiedReminder.person_name.ilike('%kusum%')).first()

if r:
    reports = [rep.strip() for rep in (r.report_types or '').split(',') if rep.strip()]
    body = build_reminder_body(reports)
    
    msg = (
        "⏰ Reminder\n\n"
        f"Hi *{r.person_name}*,\n\n"
        f"{body}\n\n"
        "Thank you! 🌱"
    )
    
    print("=== MESSAGE TO BE SENT ===")
    print(msg)
    
    res = send_waha_message("917259510983@c.us", msg)
    print("\nSend Result:", res)

db.close()
