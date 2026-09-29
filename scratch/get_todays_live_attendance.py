import sys
import os
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message

target_date = "2026-09-24"
print(f"Evaluating live attendance for today ({target_date})...")

data = evaluate_attendance_for_date(target_date)
msg = generate_attendance_summary_message(data)

print("\n=== TODAY'S LIVE ATTENDANCE REPORT (24 Sep 2026) ===")
print(msg)
