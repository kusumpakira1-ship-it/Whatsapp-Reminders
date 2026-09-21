import sys
from datetime import date
from attendance_tracker import evaluate_attendance_for_date

target_date_str = date.today().strftime('%Y-%m-%d')
print(f"=== CHECKING DATABASE FOR ATTENDANCE ON {target_date_str} ===\n")

data = evaluate_attendance_for_date(target_date_str)

for g in data['groups']:
    print(f"\n🏢 *{g['group_name']}*")
    for emp in g['employees']:
        login_str = emp.get('login_time', '-')
        logout_str = emp.get('logout_time', '-')
        nh = emp.get('net_hours', 0.0)
        print(f"  • {emp['name']} ({emp['phone']}): {emp['status_badge']} | In: {login_str} | Out: {logout_str} | Net: {nh} hrs")
