"""
Test build_7_company_escalation_reports for 14 Aug 2026 and print EOD summary text.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from scheduler import build_7_company_escalation_reports

db = SessionLocal()

target_dt = datetime.datetime(2026, 8, 14, 23, 59, 0)
msgs_930, combined_1159_text = build_7_company_escalation_reports(db, target_dt)

print("=== RE-EVALUATED 11:59 PM EOD SUMMARY REPORT FOR 14 AUG 2026 ===")
print(combined_1159_text)

db.close()

