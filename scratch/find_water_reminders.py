"""
Find Water Monitoring reminders in DB
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import UnifiedReminder, Task
from sqlalchemy import or_

db = SessionLocal()
try:
    print("=== UNIFIED REMINDERS MATCHING WATER ===")
    rems = db.query(UnifiedReminder).filter(
        or_(
            UnifiedReminder.person_name.ilike('%water%'),
            UnifiedReminder.report_types.ilike('%water%'),
            UnifiedReminder.task_notes.ilike('%water%')
        )
    ).all()
    for r in rems:
        print(f"ID: {r.id} | Name: {r.person_name} | Phone: {r.person_phone} | Group: {r.whatsapp_group_id}")
        print(f"Reports: {r.report_types} | Notes: {r.task_notes} | Active: {r.active}")
        print("-" * 60)

    print("\n=== TASKS MATCHING WATER ===")
    tasks = db.query(Task).filter(
        or_(
            Task.assigned_person_name.ilike('%water%'),
            Task.task_name.ilike('%water%'),
            Task.task_type.ilike('%water%')
        )
    ).all()
    for t in tasks:
        print(f"ID: {t.id} | Name: {t.task_name} | Assigned: {t.assigned_person_name} | Status: {t.status}")
        print("-" * 60)

finally:
    db.close()
