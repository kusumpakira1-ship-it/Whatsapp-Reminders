"""
Script to inspect yesterday's (12 Aug 2026) report submissions and escalations for all companies
"""

import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from generate_escalation_report import generate_company_escalation_reports

target_date = datetime.date(2026, 8, 12)
print(f"=== CHECKING REPORT SUBMISSIONS FOR YESTERDAY: {target_date.strftime('%d %b %Y')} ===")

reports_dict = generate_company_escalation_reports(target_date)

for company_name, report_text in reports_dict.items():
    print(f"\n==========================================")
    print(f"🏢 COMPANY: {company_name}")
    print(f"==========================================")
    print(report_text)
