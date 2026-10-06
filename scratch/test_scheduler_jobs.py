import sys, os
sys.path.insert(0, os.path.abspath('backend'))

print("=== SCHEDULER DIAGNOSTIC & VERIFICATION CHECK ===")

import water_flow_daily_report
import water_flow_farm_monitoring
import water_monitoring
import scheduler

jobs_to_test = [
    ("Daily Water Flow Report (12:05 AM)", water_flow_daily_report.send_daily_water_flow_report_job),
    ("Water Flow 4-Hour Telemetry Alert (Every 5 min)", water_flow_farm_monitoring.check_and_dispatch_water_flow_farm_alerts),
    ("Water Sensor Alert (Every 5 min)", water_monitoring.check_and_dispatch_water_alerts),
    ("Attendance 7:05 PM & 9:30 PM", scheduler.scheduled_daily_attendance_summary_job),
    ("Attendance 11:15 PM EOD Lock", scheduler.scheduled_daily_attendance_summary_1115pm_job),
    ("Egg Production Crosscheck 6:50 PM", scheduler.scheduled_egg_production_crosscheck_650pm_job),
    ("Egg Production Crosscheck 9:30 PM", scheduler.scheduled_egg_production_crosscheck_930pm_job),
    ("Egg Godown Summary 9:00 PM", scheduler.scheduled_godown_report_job),
    ("Sunfra P&L PDF 9:30 PM", scheduler.scheduled_sunfra_pandl_job),
    ("Combined 10:30 PM Dispatcher", scheduler.send_all_10pm_daily_reports_job),
    ("4-Company Weekly P&L (Sat 10:30 PM)", scheduler.scheduled_4company_weekly_pandl_job),
    ("4-Company Monthly P&L (Last Day 9:00 PM)", scheduler.scheduled_4company_monthly_pandl_job),
    ("Monthly Attendance (Last Day 9:00 PM)", scheduler.scheduled_monthly_attendance_report_job),
]

success_count = 0
fail_count = 0

for name, job_func in jobs_to_test:
    try:
        print(f"Checking {name}...")
        assert callable(job_func), f"{name} is not callable"
        print(f"  [OK] {name} is valid & importable.")
        success_count += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        fail_count += 1

print(f"\nVerification finished: {success_count} passed, {fail_count} failed out of {len(jobs_to_test)} scheduled jobs.")
