import sys

sys.path.append('backend')
from database import SessionLocal
from attendance_tracker import evaluate_attendance_for_date
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("================ TESTING STRICT GROUP ATTENDANCE RE-EVALUATION ================")

try:
    db = SessionLocal()
    # Query MySQL
    rows = db.execute(text("SELECT COUNT(*) FROM sunfra_raw_messages WHERE date(timestamp) = '2026-09-16'")).fetchone()
    print("MySQL raw messages count on 16 Sep:", rows[0])
    db.close()
    
    res = evaluate_attendance_for_date("2026-09-16")
    print("Re-evaluation complete!")
    
    db = SessionLocal()
    logs = db.execute(text("SELECT employee_name, company_name, login_time, logout_time, net_hours, status_badge, detail FROM sunfra_attendance_logs WHERE date = '2026-09-16' ORDER BY company_name, employee_name")).fetchall()
    print(f"\nTotal 16 Sep Attendance Logs: {len(logs)}")
    for l in logs:
        print(f"  • [{l[1]}] {l[0]}: Login: {l[2] or '-'} | Logout: {l[3] or '-'} | Net Hrs: {l[4]} | Badge: {l[5]} | Detail: {l[6]}")
    db.close()

except Exception as e:
    print("Error:", e)
