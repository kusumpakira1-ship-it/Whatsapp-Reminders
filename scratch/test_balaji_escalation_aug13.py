"""
Print each string in msgs_930 for Aug 13 escalation report.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from scheduler import build_7_company_escalation_reports

db = SessionLocal()
target_dt = datetime.datetime(2026, 8, 13, 21, 30)
msgs_930, msg_1159 = build_7_company_escalation_reports(db, target_dt)

print("=== 9:30 PM ESCALATION MESSAGES FOR AUG 13 ===")
for idx, text in enumerate(msgs_930):
    if 'Balaji' in text or '9493928388' in text:
        print(f"\n--- Message #{idx+1} ---\n{text}\n")

print("\n=== 11:59 PM COMBINED ESCALATION MESSAGE FOR AUG 13 ===")
for line in msg_1159.split('\n'):
    if 'Balaji' in line or 'Approval' in line or 'Work update' in line or 'Team' in line:
        print(line)

db.close()

