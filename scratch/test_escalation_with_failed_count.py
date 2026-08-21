"""
Generate EOD Escalation Report and print with failed task count headers
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, timezone, timedelta
from database import SessionLocal
from scheduler import build_7_company_escalation_reports

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

db = SessionLocal()
try:
    msgs_930, combined_1159 = build_7_company_escalation_reports(db, now_ist)
    print("============================================================")
    print("COMBINED EOD ESCALATION REPORT SUMMARY")
    print("============================================================")
    print(combined_1159)
finally:
    db.close()
