"""
Inspect Sunfra Farms section in 11:59 PM escalation report for Aug 13.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from scheduler import build_7_company_escalation_reports

db = SessionLocal()
target_dt = datetime.datetime(2026, 8, 13, 21, 30)
msgs_930, msg_1159 = build_7_company_escalation_reports(db, target_dt)

print("=== SUNFRA FARMS SECTION IN 11:59 PM ESCALATION REPORT ===")
in_farms = False
for line in msg_1159.split('\n'):
    if 'Sunfra Farms' in line:
        in_farms = True
    elif in_farms and line.startswith('7️⃣') or line.startswith('1️⃣') or line.startswith('2️⃣') or line.startswith('3️⃣') or line.startswith('4️⃣') or line.startswith('5️⃣'):
        in_farms = False
    
    if in_farms:
        print(line)

db.close()

