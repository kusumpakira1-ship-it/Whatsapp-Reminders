import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from attendance_tracker import evaluate_attendance_for_date

target_date = "2026-09-24"
data = evaluate_attendance_for_date(target_date)

print(f"=== TODAY'S EMPLOYEE ATTENDANCE DETAILS ({target_date}) ===")
for g in data['groups']:
    print(f"\n🏢 {g['group_name']}")
    for emp in g['employees']:
        print(f"  • {emp['name']} | Status: {emp['status_badge']} | Detail: {emp.get('detail', '')} | Login: {emp.get('login_time', '-')} | Logout: {emp.get('logout_time', '-')}")
