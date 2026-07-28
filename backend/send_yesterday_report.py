import sys, os
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from dotenv import load_dotenv
load_dotenv(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\.env')

import datetime
from report_generator import generate_custom_report
from waha_service import send_waha_message, send_waha_file

yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")
print(f"Generating report for {yesterday}...")

pdf_path, summary_text = generate_custom_report(yesterday)

target = "917259510983@c.us"
print(f"Sending text message to {target}...")
send_waha_message(target, summary_text)
print("Text sent.")

if pdf_path:
    # PDF path may be docker-internal — check local equivalent
    local_pdf = pdf_path.replace("/app/", r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\\")
    local_pdf = local_pdf.replace("/", "\\")
    print(f"Looking for PDF at: {local_pdf}")
    if os.path.exists(local_pdf):
        send_waha_file(target, local_pdf, caption=f"Daily Farm Summary - {yesterday}")
        print("PDF sent!")
    elif os.path.exists(pdf_path):
        send_waha_file(target, pdf_path, caption=f"Daily Farm Summary - {yesterday}")
        print("PDF sent (docker path)!")
    else:
        print(f"PDF not found at either path. Sending text only.")

print("Done!")
