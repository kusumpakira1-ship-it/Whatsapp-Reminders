import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from papaak_email_service import fetch_and_process_papaak_emails

print("Testing updated fetch_and_process_papaak_emails()...")
res = fetch_and_process_papaak_emails(notify_on_new=False)
print(f"Test completed successfully. Added {res} records.")
