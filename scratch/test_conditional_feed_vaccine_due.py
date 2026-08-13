"""
Test conditional vaccine and feed transition scheduling checks for escalations
"""

import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from models import Flock, BookStandard, Task

def check_if_vaccine_due_on_date(db, target_date):
    flocks = db.query(Flock).filter(Flock.status == 'active').all()
    for f in flocks:
        if not f.hatch_date:
            continue
        age_days = (target_date - f.hatch_date).days + 1
        if age_days < 1:
            continue
        std = db.query(BookStandard).filter(BookStandard.day == age_days).first()
        if std and std.vaccine and std.vaccine.strip():
            v_text = str(std.vaccine).strip().lower()
            if any(k in v_text for k in ['vaccine', 'nd', 'ibd', 'coryza', 'pox', 'killed', 'live', 'mareks', 'losata', 'lasata', 'vvnd', 'deworming', 'hvt', 'ma5', 'cox', 'debeaking']):
                return True
    # Also check tasks
    start_dt = datetime.datetime.combine(target_date, datetime.time.min)
    end_dt = datetime.datetime.combine(target_date, datetime.time.max)
    v_task = db.query(Task).filter(Task.due_time >= start_dt, Task.due_time <= end_dt, Task.task_name.ilike('%vaccin%')).first()
    return bool(v_task)

def check_if_feed_transition_due_on_date(db, target_date):
    flocks = db.query(Flock).filter(Flock.status == 'active').all()
    transition_weeks = {4, 9, 16, 19, 41, 71}
    for f in flocks:
        if not f.hatch_date:
            continue
        age_days = (target_date - f.hatch_date).days + 1
        if age_days < 1:
            continue
        w = (age_days - 1) // 7 + 1
        # Check if today is the exact first day of the transition week
        if (age_days - 1) % 7 == 0 and w in transition_weeks:
            return True
    start_dt = datetime.datetime.combine(target_date, datetime.time.min)
    end_dt = datetime.datetime.combine(target_date, datetime.time.max)
    f_task = db.query(Task).filter(Task.due_time >= start_dt, Task.due_time <= end_dt, Task.task_name.ilike('%feed formula%')).first()
    return bool(f_task)

db = SessionLocal()
target_date = datetime.date(2026, 8, 12)

v_due = check_if_vaccine_due_on_date(db, target_date)
f_due = check_if_feed_transition_due_on_date(db, target_date)

print(f"Date: {target_date.strftime('%d %b %Y')}")
print(f"• Vaccine Scheduled Today? {v_due}")
print(f"• Feed Transition Scheduled Today? {f_due}")

db.close()
