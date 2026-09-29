import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message

print("Evaluating attendance for 2026-09-23...")
data = evaluate_attendance_for_date("2026-09-23")
msg = generate_attendance_summary_message(data)

print("\n=== YESTERDAY'S ATTENDANCE REPORT (23 Sep 2026) ===")
print(msg)
