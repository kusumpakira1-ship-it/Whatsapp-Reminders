import os
import sys
import logging

# Ensure repo root and backend dir are in sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(repo_root, 'backend')
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# Force local WAHA URL on Windows host
os.environ["WAHA_URL"] = "http://localhost:3000"

from backend.config import settings
settings.WAHA_URL = "http://localhost:3000"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TARGET_PHONE = "917259510983@c.us"

from waha_service import send_waha_message, send_waha_file
from database import SessionLocal
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

print(f"=== SENDING ALL TODAY'S REPORTS TO {TARGET_PHONE} FOR TESTING ===")

# 1. Daily Egg Godown Summary Report (9:00 PM)
try:
    print("\n[1/10] Sending Daily Egg Godown Summary Report...")
    from report_generator_godown import generate_godown_report
    pdf_path, summary_text = generate_godown_report()
    if summary_text:
        send_waha_message(TARGET_PHONE, summary_text)
    if pdf_path and os.path.exists(pdf_path):
        send_waha_file(TARGET_PHONE, pdf_path, caption=f"Egg Godown Report - {os.path.basename(pdf_path)}")
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 2. Daily Sunfra P&L PDF Report (9:30 PM)
try:
    print("\n[2/10] Sending Daily Sunfra P&L PDF Report...")
    from sunfra_pandl_report import generate_and_send_sunfra_pandl_report
    generate_and_send_sunfra_pandl_report([TARGET_PHONE])
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 3. Daily 4-Company P&L & Stock Asset Report (9:30 PM)
try:
    print("\n[3/10] Sending Daily 4-Company P&L & Stock Asset Report...")
    from zoho_4company_pandl import generate_and_send_4company_pandl_report
    generate_and_send_4company_pandl_report(TARGET_PHONE)
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 4. Daily Egg Price & Market Analysis PDF Report (9:30 PM)
try:
    print("\n[4/10] Sending Daily Egg Price & Market Analysis PDF Report...")
    from egg_market_analyzer import send_daily_egg_market_pdf_job
    send_daily_egg_market_pdf_job()
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 5. Daily Farm Summary Report (9:30 PM)
try:
    print("\n[5/10] Sending Daily Farm Summary Report...")
    from daily_farm_summary import generate_daily_farm_summary_report
    farm_summary = generate_daily_farm_summary_report()
    if farm_summary:
        send_waha_message(TARGET_PHONE, farm_summary)
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 6. Department-Wise Manager Escalation Report (9:30 PM - 7 Messages)
try:
    print("\n[6/10] Sending 7 Department Manager Escalation Messages...")
    db = SessionLocal()
    from scheduler import build_7_company_escalation_reports
    res_esc = build_7_company_escalation_reports(db, now_ist)
    messages_930 = res_esc[0]
    combined_1159_text = res_esc[1]
    db.close()
    for idx, msg in enumerate(messages_930, 1):
        send_waha_message(TARGET_PHONE, msg)
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 7. 3-Company Zoho Reconciliation Reports (10:00 PM)
try:
    print("\n[7/10] Sending 3-Company Zoho Reconciliation Reports...")
    from zoho_reconciliation import (
        generate_and_send_zoho_reconciliation_report,
        generate_and_send_sunfra_feeds_reconciliation_report,
        generate_and_send_sunfra_corporate_reconciliation_report
    )
    generate_and_send_zoho_reconciliation_report(TARGET_PHONE)
    generate_and_send_sunfra_feeds_reconciliation_report(TARGET_PHONE)
    generate_and_send_sunfra_corporate_reconciliation_report(TARGET_PHONE)
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 8. Daily Rental & Vacancy Loss Report (10:00 PM)
try:
    print("\n[8/10] Sending Daily Rental & Vacancy Loss Report...")
    from scheduler import generate_rental_vacancy_report
    vacancy_msg = generate_rental_vacancy_report()
    if vacancy_msg:
        send_waha_message(TARGET_PHONE, vacancy_msg)
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 9. Daily Operations & Financial Summary PDF Reports (10:00 PM)
try:
    print("\n[9/10] Sending Daily Operations & Financial Summary Reports (PDF + Text)...")
    from report_generator import generate_daily_reports
    pdf_path, summary_text = generate_daily_reports()
    if summary_text:
        send_waha_message(TARGET_PHONE, summary_text)
    if pdf_path:
        pdf_paths = [pdf_path] if isinstance(pdf_path, str) else pdf_path
        for path in pdf_paths:
            caption = "Operations Report" if "operations" in path.lower() else "Financial Report" if "financial" in path.lower() else "PDF Report"
            fn = os.path.basename(path)
            send_waha_file(TARGET_PHONE, path, caption=f"{caption} - {fn}")
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

# 10. Company-Wise EOD Escalation Summary Report (11:59 PM)
try:
    print("\n[10/10] Sending 11:59 PM EOD Company-Wise Escalation Summary Report...")
    if 'combined_1159_text' in locals() and combined_1159_text:
        send_waha_message(TARGET_PHONE, combined_1159_text)
    else:
        db = SessionLocal()
        from scheduler import build_7_company_escalation_reports
        res_esc = build_7_company_escalation_reports(db, now_ist)
        combined_1159_text = res_esc[1]
        db.close()
        send_waha_message(TARGET_PHONE, combined_1159_text)
    print("  -> Success")
except Exception as e:
    print(f"  -> Error: {e}")

print("\n=== ALL REPORTS DISPATCHED TO 7259510983 ===")
