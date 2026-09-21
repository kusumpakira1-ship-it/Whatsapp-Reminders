import sys
import sqlite3
from datetime import datetime

sys.path.append('backend')
from database import get_db_session, SessionLocal
from attendance_tracker import evaluate_attendance_for_date
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("================ ENSURING ALL 30 EMPLOYEES ARE STORED FOR 16 SEP & 17 SEP ================")

for target_date in ["2026-09-16", "2026-09-17"]:
    print(f"\n--- Processing Date: {target_date} ---")
    try:
        data = evaluate_attendance_for_date(target_date)
        print(f"Successfully evaluated attendance for {target_date}!")
    except Exception as e:
        print(f"Error evaluating for {target_date}: {e}")

db = get_db_session()

print("\n================ VERIFYING 16 SEP 2026 STORED RECORDS ================")
rows_16 = db.execute(text("SELECT id, employee_name, company_name, login_time, logout_time, net_hours, status_badge FROM sunfra_attendance_logs WHERE date = '2026-09-16' ORDER BY company_name, employee_name")).fetchall()
print(f"Total 16 Sep Records in Table: {len(rows_16)}")
for r in rows_16:
    print(f"  • ID {r[0]:2d}: [{r[2]:<18}] {r[1]:<12} | Login: {r[3] or '-':<8} | Logout: {r[4] or '-':<8} | Net: {r[5]:<4} | Status: {r[6]}")

print("\n================ VERIFYING 17 SEP 2026 STORED RECORDS ================")
rows_17 = db.execute(text("SELECT id, employee_name, company_name, login_time, logout_time, net_hours, status_badge FROM sunfra_attendance_logs WHERE date = '2026-09-17' ORDER BY company_name, employee_name")).fetchall()
print(f"Total 17 Sep Records in Table: {len(rows_17)}")
for r in rows_17:
    print(f"  • ID {r[0]:2d}: [{r[2]:<18}] {r[1]:<12} | Login: {r[3] or '-':<8} | Logout: {r[4] or '-':<8} | Net: {r[5]:<4} | Status: {r[6]}")

db.close()
