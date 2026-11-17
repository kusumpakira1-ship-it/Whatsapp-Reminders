import sys, os
backend_path = r"C:/Users/sunfra/Desktop/Whatsapp Reminders/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from scheduler import send_daily_office_management_checklist_job

if __name__ == "__main__":
    send_daily_office_management_checklist_job()

