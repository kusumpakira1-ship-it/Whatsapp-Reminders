"""
Generate and print the complete 11:59 PM Combined Escalation Report for TODAY (14 Aug 2026).
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from scheduler import build_7_company_escalation_reports

db = SessionLocal()
now_ist = datetime.datetime(2026, 8, 14, 23, 59)

msgs_930, msg_1159 = build_7_company_escalation_reports(db, now_ist)

print("=== 11:59 PM COMBINED ESCALATION REPORT FOR TODAY (14 AUG 2026) ===")
print(msg_1159)

db.close()

