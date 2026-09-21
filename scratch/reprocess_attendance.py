import sys

sys.path.append('backend')
from attendance_tracker import evaluate_attendance_for_date
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("================ RE-EVALUATING ATTENDANCE FOR 16 SEP 2026 ================")
res_16 = evaluate_attendance_for_date("2026-09-16")
print("16 Sep Summary Totals:", res_16.get("summary_totals"))

print("\n================ RE-EVALUATING ATTENDANCE FOR TODAY (17 SEP 2026) ================")
res_17 = evaluate_attendance_for_date("2026-09-17")
print("17 Sep Summary Totals:", res_17.get("summary_totals"))

db = get_db_session()

print("\n================ UPDATED 16 SEP ATTENDANCE LOGS IN DATABASE ================")
rows_16 = db.execute(text("""
    SELECT employee_name, company_name, login_time, logout_time, net_hours, status_badge, detail 
    FROM sunfra_attendance_logs 
    WHERE date = '2026-09-16' 
    ORDER BY company_name, employee_name
""")).fetchall()

for r in rows_16:
    print(f"  • [{r[1]}] {r[0]}: Login: {r[2]} | Logout: {r[3]} | Net Hrs: {r[4]} | Badge: {r[5]} | Detail: {r[6]}")

print("\n================ TODAY'S (17 SEP) ATTENDANCE LOGS IN DATABASE ================")
rows_17 = db.execute(text("""
    SELECT employee_name, company_name, login_time, logout_time, net_hours, status_badge, detail 
    FROM sunfra_attendance_logs 
    WHERE date = '2026-09-17' 
    ORDER BY company_name, employee_name
""")).fetchall()

for r in rows_17:
    print(f"  • [{r[1]}] {r[0]}: Login: {r[2]} | Logout: {r[3]} | Net Hrs: {r[4]} | Badge: {r[5]} | Detail: {r[6]}")

db.close()
