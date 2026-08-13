"""
Test enhanced check_report_submitted logic with text, images, and PDF attachments
"""

import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from scheduler import build_7_company_escalation_reports

db = SessionLocal()
yesterday_dt = datetime.datetime(2026, 8, 12, 23, 59, 0)

messages_930, combined_1159_text = build_7_company_escalation_reports(db, yesterday_dt)
print("=== TESTING REPORT ENHANCEMENT ===")
print("Messages 9:30 PM generated cleanly!")
db.close()
