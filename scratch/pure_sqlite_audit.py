import sys
sys.path.insert(0, 'backend')
from database import SqliteSession
from models import RawMessage
from attendance_tracker import COMMUNITY_EMPLOYEES, evaluate_attendance_for_date

today_str = '2026-09-17'
data = evaluate_attendance_for_date(today_str)

print("="*90)
print(f"COMPLETE DATABASE LOGOUT & ATTENDANCE AUDIT ({today_str}):")
print("="*90 + "\n")

for grp in data['groups']:
    gname = grp['group_name']
    print(f"🏢 *{gname}*")
    for emp in grp['employees']:
        ename = emp['name']
        ltime = emp['login_time']
        otime = emp['logout_time']
        badge = emp['status_badge']
        detail = emp['detail']
        print(f"  • {ename:<12} | Login: {ltime:<10} | Logout: {otime:<10} | Status: {badge:<30} | Detail: {detail}")
    print("-" * 90)
