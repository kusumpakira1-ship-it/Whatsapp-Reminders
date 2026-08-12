"""
Test full vaccine approval request and group reminder logic
"""

import sys, os, datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from scheduler import SessionLocal, VACCINE_APPROVAL_PHONES, VACCINE_GROUP_JID, VACCINE_APPROVAL_KEYWORDS
from models import Flock, BookStandard

def test_preview_approval_message():
    db = SessionLocal()
    flocks = db.query(Flock).filter(Flock.status == 'active').all()
    today = datetime.date.today()
    
    print("=== CURRENT ACTIVE SHEDS AND AGES ===")
    for f in flocks:
        age_days = (today - f.hatch_date).days + 1
        w = (age_days - 1) // 7 + 1
        std = db.query(BookStandard).filter(BookStandard.day == age_days).first()
        vacc = std.vaccine if std and std.vaccine else "No vaccine scheduled today"
        print(f"• {f.shed_name}: Day {age_days} (Week {w}) | Today Vaccine: {vacc}")
        
    db.close()

test_preview_approval_message()
