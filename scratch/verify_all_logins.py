import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from attendance_tracker import evaluate_attendance_for_date

data = evaluate_attendance_for_date()

with open(os.path.join(os.path.dirname(__file__), "all_logins_verified.txt"), "w", encoding="utf-8") as f:
    f.write(f"=== VERIFIED ATTENDANCE FOR {data['date']} ===\n\n")
    for g in data['groups']:
        f.write(f"🏢 Group: {g['group_name']}\n")
        for emp in g['employees']:
            f.write(f"  • {emp['name']}: {emp['status_badge']} | Detail: {emp['detail']}\n")
        f.write("\n")

print("All logins verified and written.")
