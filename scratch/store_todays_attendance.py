import sys
import time

sys.path.append('backend')
from database import get_db_session
from attendance_tracker import evaluate_attendance_for_date
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("================ EVALUATING & STORING TODAY'S (17 SEP 2026) ATTENDANCE ================")

max_retries = 3
for attempt in range(max_retries):
    try:
        db = get_db_session()
        # Test query
        res = db.execute(text("SELECT COUNT(*) FROM sunfra_raw_messages WHERE date(timestamp) = '2026-09-17'")).fetchone()
        print(f"Raw messages logged today (17 Sep 2026): {res[0]}")
        db.close()
        
        # Evaluate & Upsert today's attendance into sunfra_attendance_logs table
        result_data = evaluate_attendance_for_date("2026-09-17")
        print("Attendance evaluation for 17 Sep complete!")
        
        # Verify stored rows in sunfra_attendance_logs
        db = get_db_session()
        logs = db.execute(text("SELECT id, employee_name, company_name, login_time, logout_time, status_badge, detail FROM sunfra_attendance_logs WHERE date = '2026-09-17' ORDER BY company_name, employee_name")).fetchall()
        print(f"\nTotal rows stored in sunfra_attendance_logs for today (17 Sep): {len(logs)}")
        for l in logs:
            print(f"  • ID {l[0]}: [{l[2]}] {l[1]} | Login: {l[3] or '-'} | Logout: {l[4] or '-'} | Status: {l[5]}")
        db.close()
        break

    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        time.sleep(3)
