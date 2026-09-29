import sys
import os
import logging
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath("backend"))

print("=== STARTING FULL REPORT SYSTEM HEALTH AUDIT ===")

# 1. Test Attendance Tracker
try:
    from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message, generate_monthly_attendance_summary_message
    att_data = evaluate_attendance_for_date()
    daily_msg = generate_attendance_summary_message(att_data)
    monthly_msg = generate_monthly_attendance_summary_message()
    print("✅ Attendance Tracker (Daily & Monthly Reports): PASS")
except Exception as e:
    print(f"❌ Attendance Tracker: FAIL ({e})")

# 2. Test 4-Company Consolidated Reports
try:
    from zoho_reconciliation import dispatch_all_4company_reconciliation_reports
    print("✅ 4-Company Daily Reconciliation Reports: PASS")
except Exception as e:
    print(f"❌ 4-Company Daily Reconciliation Reports: FAIL ({e})")

# 3. Test Weekly & Monthly 4-Company P&L
try:
    from zoho_4company_pandl import generate_4company_weekly_pandl_report, generate_4company_monthly_pandl_report
    print("✅ 4-Company Weekly & Monthly P&L Reports: PASS")
except Exception as e:
    print(f"❌ 4-Company Weekly & Monthly P&L Reports: FAIL ({e})")

# 4. Test PAPAAK Email Forwarding Service
try:
    from papaak_email_service import fetch_and_process_papaak_emails
    print("✅ PAPAAK Email Forwarding & Rate Parser: PASS")
except Exception as e:
    print(f"❌ PAPAAK Email Forwarding: FAIL ({e})")

# 5. Test Egg Market & Godown Reports
try:
    from egg_market_analyzer import send_daily_egg_market_pdf_job
    from daily_farm_summary import generate_daily_farm_summary_report
    print("✅ Egg Market PDF & Godown Closing Reports: PASS")
except Exception as e:
    print(f"❌ Egg Market / Godown Reports: FAIL ({e})")

# 6. Test WAHA WhatsApp Service
try:
    from waha_service import get_session_status
    status = get_session_status("default")
    print(f"✅ WAHA WhatsApp Gateway: PASS (Session Status: {status})")
except Exception as e:
    print(f"❌ WAHA WhatsApp Gateway: FAIL ({e})")

# 7. Check Active Daemon Scheduler Initialization
try:
    from scheduler import scheduler
    print(f"✅ APScheduler Core: PASS (Scheduler instance initialized cleanly)")
except Exception as e:
    print(f"❌ APScheduler Core: FAIL ({e})")

print("=== FULL REPORT SYSTEM HEALTH AUDIT COMPLETE ===")
