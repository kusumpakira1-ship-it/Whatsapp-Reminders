import sys
sys.path.insert(0, 'backend')
import logging
logging.basicConfig(level=logging.INFO)

print("Checking availability of all scheduled evening report functions in scheduler.py...")

try:
    from scheduler import (
        scheduled_4company_consolidated_reports_job,
        scheduled_egg_production_crosscheck_650pm_job,
        scheduled_godown_report_job,
        scheduled_egg_production_crosscheck_930pm_job,
        scheduled_daily_attendance_summary_job,
        send_all_10pm_daily_reports_job
    )
    print("✅ All 6 evening job functions imported successfully!")
except Exception as e:
    print("❌ Import failed:", e)

# Test evaluate_attendance_for_date for tonight's 9:30 PM report
try:
    from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message
    res = evaluate_attendance_for_date('2026-09-17')
    print("✅ Attendance evaluation for 17 Sep 2026 runs cleanly. Total employees:", res.get('total_employees'))
except Exception as e:
    print("❌ Attendance evaluation test failed:", e)
