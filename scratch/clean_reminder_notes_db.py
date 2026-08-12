"""
Update all existing reminders in sunfra_unified_reminders table:
Convert paragraph task_notes into clean bullet points for multi-report reminders.
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from models import UnifiedReminder

def format_report_name(r: str) -> str:
    if not r: return ""
    words = str(r).strip().split()
    formatted = []
    for w in words:
        wl = w.lower()
        if wl in ['p&l', 'p/l', 'p-and-l']: formatted.append('P&L')
        elif wl in ['ca']: formatted.append('CA')
        elif wl in ['eod']: formatted.append('EOD')
        else: formatted.append(w.capitalize())
    return " ".join(formatted)

db = SessionLocal()

reminders = db.query(UnifiedReminder).all()
updated_count = 0

for r in reminders:
    reports = [rep.strip() for rep in (r.report_types or '').split(',') if rep.strip()]
    if not reports:
        continue
        
    formatted_reports = [format_report_name(rep) for rep in reports]
    
    if len(formatted_reports) == 1:
        new_notes = f"Please submit today's *{formatted_reports[0]}* Report so the daily records and reports can be completed accurately."
    else:
        bullets = "\n".join(f"  • *{rep}*" for rep in formatted_reports)
        new_notes = f"Please submit the following pending reports for today:\n{bullets}"
        
    if r.task_notes != new_notes:
        print(f"Updating Reminder ID {r.id} ({r.person_name}):")
        print(f"  OLD Notes: {r.task_notes}")
        print(f"  NEW Notes:\n{new_notes}\n")
        r.task_notes = new_notes
        updated_count += 1

db.commit()
db.close()

print(f"✅ Cleaned up task_notes for {updated_count} reminders in database!")
