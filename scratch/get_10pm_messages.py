"""
Generate and print exact 10:00 PM reports (Daily Farm Summary & Escalation Report)
"""
import sys, os
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

print("============================================================")
print("1️⃣ 10:00 PM DAILY FARM SUMMARY REPORT")
print("============================================================")

try:
    from report_generator import generate_daily_reports
    pdf_path, summary_text = generate_daily_reports()
    print(summary_text)
except Exception as e:
    print(f"Error generating 10 PM daily report: {e}")

print("\n============================================================")
print("2️⃣ EOD COMPANY-WISE ESCALATION REPORT")
print("============================================================")

try:
    from scheduler import build_eod_escalation_report
    # Or call escalation check logic
except Exception as e:
    pass

