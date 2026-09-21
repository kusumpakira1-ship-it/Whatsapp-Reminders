import os
import sys

backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

from database import engine, sqlite_engine, Base, get_db_session
from models import DailyAttendance
from attendance_tracker import evaluate_attendance_for_date
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')

print("==================================================")
print("🛠️ CREATING / VERIFYING TABLE: sunfra_attendance_logs")
print("==================================================")

try:
    Base.metadata.create_all(bind=engine)
    print("✅ MySQL table sunfra_attendance_logs verified/created.")
except Exception as e:
    print(f"⚠️ MySQL table creation warning: {e}")

try:
    Base.metadata.create_all(bind=sqlite_engine)
    print("✅ SQLite table sunfra_attendance_logs verified/created.")
except Exception as e:
    print(f"⚠️ SQLite table creation warning: {e}")

print("\n--- Running Attendance Sync for Today ---")
res = evaluate_attendance_for_date()
print(f"Sync complete. Total employees processed: {res['total_employees']}")

print("\n--- Querying DB Table sunfra_attendance_logs ---")
db = get_db_session()

today_date = date.today()
records = db.query(DailyAttendance).filter(DailyAttendance.date == today_date).order_by(DailyAttendance.company_name, DailyAttendance.employee_name).all()

print(f"\nFound {len(records)} records in DB table for {today_date}:")
print(f"{'Company':<18} | {'Group JID':<25} | {'Name':<12} | {'Login':<8} | {'Lunch Out':<9} | {'Lunch Back':<10} | {'Logout':<8} | {'Status':<25}")
print("-" * 140)

for r in records:
    c_name = r.company_name or ""
    g_jid = r.group_id or "-"
    e_name = r.employee_name or ""
    l_in = r.login_time or "-"
    lu_out = r.lunch_start_time or "-"
    lu_in = r.lunch_end_time or "-"
    l_out = r.logout_time or "-"
    st = r.status_badge or "-"
    print(f"{c_name:<18} | {g_jid:<25} | {e_name:<12} | {l_in:<8} | {lu_out:<9} | {lu_in:<10} | {l_out:<8} | {st:<25}")

db.close()
