import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from papaak_email_service import fetch_and_process_papaak_emails

print("Executing fetch_and_process_papaak_emails(notify_on_new=True)...")
count = fetch_and_process_papaak_emails(notify_on_new=True)
print(f"Finished processing. New rate records added: {count}")
