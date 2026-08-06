import sys
import logging

logging.basicConfig(level=logging.INFO)

print("=== STARTING FULL BACKEND REPORT JOBS AUDIT ===")

# 1. Test Sunfra P&L Job
try:
    from sunfra_pandl_report import generate_and_send_sunfra_pandl_report
    res_pandl = generate_and_send_sunfra_pandl_report("917259510983@c.us")
    print(f"[1] Sunfra P&L PDF Job (9:29 PM IST): {'SUCCESS' if res_pandl else 'FAILED'}")
except Exception as e:
    print(f"[1] Sunfra P&L PDF Job: ERROR ({e})")

# 2. Test 10:00 PM Daily Consolidated Reports
try:
    from report_generator import generate_daily_report, send_daily_report
    # Generate daily report
    report_text = generate_daily_report()
    print(f"[2] Daily Consolidated Report Generator: {'SUCCESS' if report_text else 'EMPTY'}")
    if report_text:
        print("    Report Snippet:\n", report_text[:300])
except Exception as e:
    print(f"[2] Daily Consolidated Report: ERROR ({e})")

# 3. Test Zoho Reconciliation Report
try:
    from report_generator import generate_zoho_reconciliation_report
    zoho_rep = generate_zoho_reconciliation_report()
    print(f"[3] Zoho Reconciliation Report Generator: {'SUCCESS' if zoho_rep else 'EMPTY'}")
    if zoho_rep:
        print("    Zoho Report Snippet:\n", str(zoho_rep)[:300])
except Exception as e:
    print(f"[3] Zoho Reconciliation Report: ERROR ({e})")

print("=== FULL AUDIT COMPLETE ===")
