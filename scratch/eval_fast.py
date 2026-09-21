import sys
sys.path.insert(0, 'backend')
from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message

data = evaluate_attendance_for_date('2026-09-17')
msg = generate_attendance_summary_message(data)
print(msg)
