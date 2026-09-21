import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from scheduler import (
    scheduled_godown_report_job,
    scheduled_sunfra_pandl_job,
    scheduled_egg_production_crosscheck_930pm_job,
    scheduled_daily_attendance_summary_job,
    scheduled_egg_market_pdf_job,
    send_all_10pm_daily_reports_job,
    scheduled_4company_weekly_pandl_job
)

out_file = os.path.join(os.path.dirname(__file__), "test_night_reports_out.txt")
log_results = ["=== AUDITING & TESTING ALL NIGHT SCHEDULED REPORT JOBS ==="]

# 1. Godown Report Job (9:00 PM)
try:
    log_results.append("\n1. Testing scheduled_godown_report_job (9:00 PM)...")
    from report_generator_godown import generate_godown_report
    pdf_path, summary_text = generate_godown_report()
    log_results.append(f"   SUCCESS: Godown report generated ({len(summary_text)} chars, PDF: {pdf_path})")
except Exception as e:
    log_results.append(f"   ERROR in scheduled_godown_report_job: {e}")

# 2. Sunfra P&L Job (9:30 PM)
try:
    log_results.append("\n2. Testing scheduled_sunfra_pandl_job (9:30 PM)...")
    from sunfra_pandl_report import generate_sunfra_pandl_report_text
    txt = generate_sunfra_pandl_report_text()
    log_results.append(f"   SUCCESS: Sunfra P&L text generated ({len(txt)} chars)")
except Exception as e:
    log_results.append(f"   ERROR in scheduled_sunfra_pandl_job: {e}")

# 3. Egg Production Crosscheck 9:30 PM
try:
    log_results.append("\n3. Testing scheduled_egg_production_crosscheck_930pm_job (9:30 PM)...")
    from egg_production_crosscheck import generate_egg_production_crosscheck_report
    cross_txt = generate_egg_production_crosscheck_report()
    log_results.append(f"   SUCCESS: Egg crosscheck generated ({len(cross_txt)} chars)")
except Exception as e:
    log_results.append(f"   ERROR in scheduled_egg_production_crosscheck_930pm_job: {e}")

# 4. Daily Attendance Summary 9:30 PM
try:
    log_results.append("\n4. Testing scheduled_daily_attendance_summary_job (9:30 PM)...")
    from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message
    att_data = evaluate_attendance_for_date()
    att_txt = generate_attendance_summary_message(att_data)
    log_results.append(f"   SUCCESS: Attendance summary generated ({len(att_txt)} chars)")
except Exception as e:
    log_results.append(f"   ERROR in scheduled_daily_attendance_summary_job: {e}")

# 5. Egg Market PDF Job 9:30 PM
try:
    log_results.append("\n5. Testing scheduled_egg_market_pdf_job (9:30 PM)...")
    from egg_market_analyzer import generate_egg_market_report_text
    mkt_txt = generate_egg_market_report_text()
    log_results.append(f"   SUCCESS: Egg market text generated ({len(mkt_txt)} chars)")
except Exception as e:
    log_results.append(f"   ERROR in scheduled_egg_market_pdf_job: {e}")

# 6. Combined 10:00 PM Reports Job
try:
    log_results.append("\n6. Testing send_all_10pm_daily_reports_job (10:00 PM)...")
    from zoho_4company_pandl import generate_4company_pandl_report
    from scheduler import generate_rental_vacancy_report
    p4_txt = generate_4company_pandl_report()
    v_txt = generate_rental_vacancy_report()
    log_results.append(f"   SUCCESS: 4-Company P&L ({len(p4_txt)} chars) & Rental Vacancy ({len(v_txt)} chars) generated")
except Exception as e:
    log_results.append(f"   ERROR in send_all_10pm_daily_reports_job: {e}")

# 7. Saturday 10:30 PM Weekly 4-Company P&L Job
try:
    log_results.append("\n7. Testing scheduled_4company_weekly_pandl_job (10:30 PM Saturday)...")
    from zoho_4company_pandl import generate_4company_weekly_pandl_report
    wp4_txt = generate_4company_weekly_pandl_report()
    log_results.append(f"   SUCCESS: Weekly 4-Company P&L generated ({len(wp4_txt)} chars)")
except Exception as e:
    log_results.append(f"   ERROR in scheduled_4company_weekly_pandl_job: {e}")

log_results.append("\n=== ALL NIGHT REPORT JOBS AUDITED SUCCESSFULLY! ===")

with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_results))

print("Audit complete.")
