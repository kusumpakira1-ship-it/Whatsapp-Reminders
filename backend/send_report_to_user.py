import os
import sys
from report_generator_godown import generate_godown_report
from waha import send_waha_message, send_waha_file

print("Generating report...")
pdf_path, summary_text = generate_godown_report()

phone = "917975209680"
print(f"Sending to {phone}...")

send_waha_message(phone, summary_text)

if pdf_path and os.path.exists(pdf_path):
    send_waha_file(phone, pdf_path, caption=f"Egg Godown Report - {os.path.basename(pdf_path)}")
    
print("Done!")
