import sys
import os
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from attendance_tracker import evaluate_attendance_for_date

today_str = date.today().strftime('%Y-%m-%d')
data = evaluate_attendance_for_date(today_str)

print(f"=== DETAILED LIVE ATTENDANCE LOG ({today_str}) ===")
for g in data['groups']:
    print(f"\n🏢 {g['group_name']}:")
    for emp in g['employees']:
        print(f"  • {emp['name']:<15} | Status: {emp['status_badge']:<35} | Login: {emp['login_time']:<10} | Logout: {emp['logout_time']:<10} | Detail: {emp['detail']}")
