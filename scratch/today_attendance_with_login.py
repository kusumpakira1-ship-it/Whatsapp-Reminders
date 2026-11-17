import sys, os
backend_path = r"C:/Users/sunfra/Desktop/Whatsapp Reminders/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message
from datetime import datetime

def main():
    data = evaluate_attendance_for_date()
    print('--- Detailed Attendance for', data.get('date'), '---')
    for group in data.get('groups', []):
        print(f"\n🏢 {group.get('group_name')}")
        for emp in group.get('employees', []):
            name = emp.get('name')
            ab = emp.get('ab')
            status = emp.get('presence')
            login = emp.get('login_time') if emp.get('login_time') else '-'
            print(f"  • {name} (Ab - {ab}) : {status} | Login: {login}")
    # also print summary
    print('\n--- Summary ---')
    print(generate_attendance_summary_message(data))

if __name__ == '__main__':
    main()

