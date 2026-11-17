import sys, os
# Ensure backend path is on sys.path
backend_path = r"C:/Users/sunfra/Desktop/Whatsapp Reminders/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message, generate_company_attendance_messages

def main():
    data = evaluate_attendance_for_date()
    summary = generate_attendance_summary_message(data)
    print("--- Summary ---")
    print(summary)
    company_msgs = generate_company_attendance_messages(data)
    print("--- Company Messages ---")
    for msg in company_msgs:
        print(msg)

if __name__ == "__main__":
    main()

