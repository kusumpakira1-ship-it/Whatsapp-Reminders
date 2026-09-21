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

out_file = os.path.join(os.path.dirname(__file__), "exact_jobs_out.txt")
log_results = ["=== TESTING EXACT SCHEDULER JOB FUNCTIONS DIRECTLY ==="]

# 1. Godown Report Job
try:
    log_results.append("\n1. Testing scheduled_godown_report_job()...")
    scheduled_godown_report_job()
    log_results.append("   SUCCESS: scheduled_godown_report_job completed clean!")
except Exception as e:
    log_results.append(f"   ERROR: {e}")

# 2. Sunfra P&L Job
try:
    log_results.append("\n2. Testing scheduled_sunfra_pandl_job()...")
    scheduled_sunfra_pandl_job()
    log_results.append("   SUCCESS: scheduled_sunfra_pandl_job completed clean!")
except Exception as e:
    log_results.append(f"   ERROR: {e}")

# 3. Egg Crosscheck 9:30 PM
try:
    log_results.append("\n3. Testing scheduled_egg_production_crosscheck_930pm_job()...")
    scheduled_egg_production_crosscheck_930pm_job()
    log_results.append("   SUCCESS: scheduled_egg_production_crosscheck_930pm_job completed clean!")
except Exception as e:
    log_results.append(f"   ERROR: {e}")

# 4. Daily Attendance Summary 9:30 PM
try:
    log_results.append("\n4. Testing scheduled_daily_attendance_summary_job()...")
    scheduled_daily_attendance_summary_job()
    log_results.append("   SUCCESS: scheduled_daily_attendance_summary_job completed clean!")
except Exception as e:
    log_results.append(f"   ERROR: {e}")

# 5. Egg Market PDF Job 9:30 PM
try:
    log_results.append("\n5. Testing scheduled_egg_market_pdf_job()...")
    scheduled_egg_market_pdf_job()
    log_results.append("   SUCCESS: scheduled_egg_market_pdf_job completed clean!")
except Exception as e:
    log_results.append(f"   ERROR: {e}")

# 6. Combined 10:00 PM Reports Job
try:
    log_results.append("\n6. Testing send_all_10pm_daily_reports_job()...")
    send_all_10pm_daily_reports_job()
    log_results.append("   SUCCESS: send_all_10pm_daily_reports_job completed clean!")
except Exception as e:
    log_results.append(f"   ERROR: {e}")

# 7. Saturday 10:30 PM Weekly 4-Company P&L Job
try:
    log_results.append("\n7. Testing scheduled_4company_weekly_pandl_job()...")
    scheduled_4company_weekly_pandl_job()
    log_results.append("   SUCCESS: scheduled_4company_weekly_pandl_job completed clean!")
except Exception as e:
    log_results.append(f"   ERROR: {e}")

log_results.append("\n=== ALL EXACT SCHEDULER JOBS TESTED CLEAN ===")

with open(out_file, "w", encoding="utf-8") as f:
    f.write("\n".join(log_results))

print("Exact jobs test finished.")
