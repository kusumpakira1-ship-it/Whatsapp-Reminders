"""
Test EOD Escalation Report for 17 Aug 2026
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from datetime import date
from scheduler import build_7_company_escalation_reports

reports = build_7_company_escalation_reports(target_date=date(2026, 8, 17))
for idx, (rep_id, phone, text) in enumerate(reports, 1):
    print(f"=== REPORT #{idx} (Phone: {phone}) ===")
    print(text)
    print("=" * 60)
