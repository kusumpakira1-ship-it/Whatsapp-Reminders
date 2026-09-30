import sys
import os
import datetime

# Add backend directory to sys.path
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal, get_db_session
from scheduler import build_7_company_escalation_reports

db = get_db_session()
# Target date: Sep 29, 2026
target_date = datetime.datetime(2026, 9, 29, 23, 59, 59)

try:
    msgs_930, msgs_1159, msg_combined = build_7_company_escalation_reports(db, target_date)
    
    print("=================== SEP 29, 2026 COMBINED EOD ESCALATION REPORT ===================")
    print(msg_combined)
    print("\n=================== SEP 29, 2026 PER-COMPANY 11:59 PM MESSAGES ===================")
    for idx, msg in enumerate(msgs_1159, 1):
        print(f"\n--- Company Message {idx} ---\n{msg}\n")
    print("\n=================== SEP 29, 2026 PER-COMPANY 9:30 PM MESSAGES ===================")
    for idx, msg in enumerate(msgs_930, 1):
        print(f"\n--- Section 9:30 PM #{idx} ---\n{msg}\n")

finally:
    db.close()
