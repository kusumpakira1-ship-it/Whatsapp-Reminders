import sys
import os

sys.path.insert(0, os.path.abspath("backend"))

from attendance_tracker import generate_monthly_attendance_summary_message
from waha_service import send_waha_message

if __name__ == "__main__":
    msg = generate_monthly_attendance_summary_message()
    res = send_waha_message("917259510983@c.us", msg)
    print(f"Sent monthly attendance report to 917259510983@c.us. Result: {res}")
