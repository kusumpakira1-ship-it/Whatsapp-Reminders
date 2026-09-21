import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message, generate_company_attendance_messages
from waha_service import send_waha_message

data = evaluate_attendance_for_date()

# 1. Send complete consolidated report across all companies to Kusum (7259510983)
summary_msg = generate_attendance_summary_message(data)
res_summary = send_waha_message("917259510983@c.us", summary_msg)
print(f"Consolidated Summary sent to 7259510983: {res_summary}")

# 2. Send company-wise attendance reports to Kusum (7259510983)
company_msgs = generate_company_attendance_messages(data)
sent_count = 0
for comp_name, comp_msg in company_msgs.items():
    r = send_waha_message("917259510983@c.us", comp_msg)
    if r:
        sent_count += 1
print(f"Company-wise reports sent to 7259510983: {sent_count}/{len(company_msgs)}")

# Output report to text file for inspection
with open(os.path.join(os.path.dirname(__file__), "todays_attendance_out.txt"), "w", encoding="utf-8") as f:
    f.write("=== CONSOLIDATED SUMMARY ===\n")
    f.write(summary_msg + "\n\n")
    f.write("=== COMPANY-WISE REPORTS ===\n")
    for comp_name, comp_msg in company_msgs.items():
        f.write(f"\n--- {comp_name} ---\n")
        f.write(comp_msg + "\n")
