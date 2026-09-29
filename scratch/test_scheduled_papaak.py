import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from scheduler import scheduled_papaak_email_fetch_job

print("Running scheduled_papaak_email_fetch_job()...")
scheduled_papaak_email_fetch_job()
print("Execution completed successfully.")
