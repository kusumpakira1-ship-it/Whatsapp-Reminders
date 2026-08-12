"""
Script to test vaccine approval request dispatch
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from scheduler import scheduled_vaccine_approval_request_job

print("=== TRIGGERING VACCINE APPROVAL REQUEST JOB ===")
scheduled_vaccine_approval_request_job()
print("DONE: Approval request dispatched to approvers!")
