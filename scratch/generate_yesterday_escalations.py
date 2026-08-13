"""
Generate exact 12 August 2026 report submissions (submitted vs missing) for all 7 companies
"""

import sys, os, datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from scheduler import build_7_company_escalation_reports

db = SessionLocal()
yesterday_dt = datetime.datetime(2026, 8, 12, 23, 59, 0)

messages_930, combined_1159_text = build_7_company_escalation_reports(db, yesterday_dt)

print("=========================================================================")
print("📊 YESTERDAY'S REPORT SUBMISSION CHECK (12 AUGUST 2026)")
print("=========================================================================\n")

for idx, msg in enumerate(messages_930, 1):
    print(f"--- Company {idx}/7 ---")
    print(msg)
    print("\n" + "-"*50 + "\n")

print("\n=========================================================================")
print("📊 COMBINED 11:59 PM EOD REPORT SUMMARY (12 AUGUST 2026)")
print("=========================================================================\n")
print(combined_1159_text)

db.close()
