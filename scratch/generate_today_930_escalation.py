"""
Generate today's (13 August 2026) 9:30 PM Escalation Reports for all 7 companies
"""

import sys, os, datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from scheduler import build_7_company_escalation_reports

db = SessionLocal()
now_dt = datetime.datetime.now()

messages_930, combined_1159_text = build_7_company_escalation_reports(db, now_dt)

print("=== TODAY'S 9:30 PM ESCALATION REPORTS (13 AUGUST 2026) ===")
for idx, msg in enumerate(messages_930, 1):
    print(f"\n--- MESSAGE {idx}/7 ---")
    print(msg)

db.close()
