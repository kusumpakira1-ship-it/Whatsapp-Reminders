"""
Inspect UnifiedReminder and Task tables to examine sub_reports_status and status
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import json
from database import SessionLocal
from models import UnifiedReminder, Task

db = SessionLocal()
try:
    print("=== UNIFIED REMINDERS ===")
    rems = db.query(UnifiedReminder).all()
    for r in rems:
        print(f"ID: {r.id} | Title: {r.report_types} | Group: {r.whatsapp_group_id} | Status: {r.status}")
        print(f"SubReportsStatus: {r.sub_reports_status}")
        print("-" * 50)

    print("\n=== TASKS ===")
    tasks = db.query(Task).all()
    for t in tasks:
        print(f"ID: {t.id} | Name: {t.task_name} | Status: {t.status}")
        print(f"SubReportsStatus: {t.sub_reports_status}")
        print("-" * 50)
finally:
    db.close()
