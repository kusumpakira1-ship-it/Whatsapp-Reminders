import sys
sys.path.insert(0, 'backend')
from database import SqliteSession
from models import RawMessage
from attendance_tracker import evaluate_attendance_for_date

today_str = '2026-09-17'
data = evaluate_attendance_for_date(today_str)

print(f"COMPREHENSIVE LOGOUT AUDIT FOR ALL 31 EMPLOYEES ({today_str}):\n")

for grp in data['groups']:
    gname = grp['group_name']
    print(f"=== 🏢 {gname} ===")
    for emp in grp['employees']:
        ename = emp['name']
        ltime = emp['login_time']
        otime = emp['logout_time']
        badge = emp['status_badge']
        detail = emp['detail']
        print(f"  {ename:<12} | Login: {ltime:<10} | Logout: {otime:<10} | Badge: {badge:<32} | Detail: {detail}")
