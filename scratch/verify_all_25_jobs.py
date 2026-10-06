import sys, os
sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')

print("=== VERIFYING ALL 25 JOBS IN SETUP_SCHEDULER ===")

import scheduler

# Force test setup_scheduler imports
from sunfra_batch_sync import sync_flocks_from_sunfra_web
from water_monitoring import check_and_dispatch_water_alerts
from water_flow_farm_monitoring import check_and_dispatch_water_flow_farm_alerts
from water_flow_daily_report import send_daily_water_flow_report_job

jobs_map = {
    "1. Health Monitor": getattr(scheduler, "health_monitor_job", None),
    "2. PAPAAK Email Fetcher": getattr(scheduler, "scheduled_papaak_email_fetch_job", None),
    "3. Sunfra Flock Web Sync": sync_flocks_from_sunfra_web,
    "4. Daily Sunfra P&L PDF (9:30 PM)": getattr(scheduler, "scheduled_sunfra_pandl_job", None),
    "5. Monday Feed Reminder": getattr(scheduler, "send_monday_weekly_feed_reminder_job", None),
    "6. Task Overdue Checker": getattr(scheduler, "poll_and_remind_tasks_job", None),
    "7. Daily Egg Godown Report (9:00 PM)": getattr(scheduler, "scheduled_godown_report_job", None),
    "8. Midnight Reset": getattr(scheduler, "midnight_reset_job", None),
    "9. Old Files Cleanup": getattr(scheduler, "cleanup_old_files_job", None),
    "10. 4-Company Consolidated Reports (6:50 PM)": getattr(scheduler, "scheduled_4company_consolidated_reports_job", None),
    "11. Egg Production Crosscheck (6:50 PM)": getattr(scheduler, "scheduled_egg_production_crosscheck_650pm_job", None),
    "12. Egg Production Crosscheck (9:30 PM)": getattr(scheduler, "scheduled_egg_production_crosscheck_930pm_job", None),
    "13. Attendance Summary (7:05 PM)": getattr(scheduler, "scheduled_daily_attendance_summary_job", None),
    "14. Attendance Summary (9:30 PM)": getattr(scheduler, "scheduled_daily_attendance_summary_job", None),
    "15. Attendance Summary EOD Lock (11:15 PM)": getattr(scheduler, "scheduled_daily_attendance_summary_1115pm_job", None),
    "16. Combined 10:30 PM Dispatcher": getattr(scheduler, "send_all_10pm_daily_reports_job", None),
    "17. 4-Company Weekly P&L (Sat 10:30 PM)": getattr(scheduler, "scheduled_4company_weekly_pandl_job", None),
    "18. 4-Company Monthly P&L (Last Day 9:00 PM)": getattr(scheduler, "scheduled_4company_monthly_pandl_job", None),
    "19. Monthly Attendance Report (Last Day 9:00 PM)": getattr(scheduler, "scheduled_monthly_attendance_report_job", None),
    "20. Weekly Operations Report (Sun 11:00 PM)": getattr(scheduler, "scheduled_weekly_report_job", None),
    "21. Monthly Operations Report (1st 11:00 PM)": getattr(scheduler, "scheduled_monthly_report_job", None),
    "22. Yearly Operations Report (Dec 31 11:00 PM)": getattr(scheduler, "scheduled_yearly_report_job", None),
    "23. Water Monitoring Sensor Alerts": check_and_dispatch_water_alerts,
    "24. Water Flow 4-Hour Telemetry Alert": check_and_dispatch_water_flow_farm_alerts,
    "25. Daily Water Flow Summary Report (12:05 AM)": send_daily_water_flow_report_job
}

pass_cnt = 0
fail_cnt = 0

for name, fn in jobs_map.items():
    if fn is not None and callable(fn):
        print(f"✅ {name}: Valid & Importable")
        pass_cnt += 1
    else:
        print(f"❌ {name}: MISSING OR INVALID")
        fail_cnt += 1

print(f"\n==========================================")
print(f"FINAL AUDIT VERDICT: {pass_cnt} PASSED, {fail_cnt} FAILED out of {len(jobs_map)} JOBS.")
print(f"==========================================")
