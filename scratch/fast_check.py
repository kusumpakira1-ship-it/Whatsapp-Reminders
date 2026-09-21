import sys

sys.path.append('backend')
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

print("================ CHECKING CURRENT ATTENDANCE LOGS FOR 16 SEP ================")
rows_16 = db.execute(text("""
    SELECT employee_name, company_name, login_time, logout_time, net_hours, status_badge, detail 
    FROM sunfra_attendance_logs 
    WHERE date = '2026-09-16' 
    ORDER BY company_name, employee_name
""")).fetchall()

for r in rows_16:
    print(f"  • [{r[1]}] {r[0]}: Login: {r[2]} | Logout: {r[3]} | Net Hrs: {r[4]} | Badge: {r[5]} | Detail: {r[6]}")

db.close()
