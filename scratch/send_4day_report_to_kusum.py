import sys
import os

sys.path.insert(0, os.path.abspath("backend"))

from waha_service import send_waha_message

if __name__ == "__main__":
    with open("scratch/four_day_report.txt", "r", encoding="utf-8") as f:
        msg = f.read()
    
    res = send_waha_message("917259510983@c.us", msg)
    print(f"Sent 4-day attendance report to 917259510983@c.us. Result: {res}")
