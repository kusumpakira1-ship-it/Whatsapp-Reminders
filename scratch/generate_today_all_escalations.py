"""
Generate and print ALL 9:30 PM (manager-wise) and 11:59 PM (combined) escalation reports for TODAY (14 Aug 2026).
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from scheduler import build_7_company_escalation_reports

db = SessionLocal()
now_ist = datetime.datetime(2026, 8, 14, 14, 11)

msgs_930, msg_1159 = build_7_company_escalation_reports(db, now_ist)

print("=== 9:30 PM MANAGER-WISE ESCALATION MESSAGES FOR TODAY (14 AUG 2026) ===")
for idx, text in enumerate(msgs_930):
    print(f"\n--- Message #{idx+1} ---\n{text}\n")

print("\n=== 11:59 PM COMBINED ESCALATION REPORT FOR TODAY (14 AUG 2026) ===")
print(msg_1159)

db.close()

