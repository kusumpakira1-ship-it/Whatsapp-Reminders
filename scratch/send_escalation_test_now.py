"""
Script to dispatch both 9:30 PM (7 messages) and 11:59 PM (1 message) escalation reports to 7259510983 right now.
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from scheduler import manager_escalation_job, company_wise_escalation_job

print("=== DISPATCHING 9:30 PM ESCALATION REPORTS (7 MESSAGES) NOW ===")
manager_escalation_job()

print("\n=== DISPATCHING 11:59 PM COMBINED ESCALATION REPORT (1 MESSAGE) NOW ===")
company_wise_escalation_job()

print("\nSUCCESS: All escalation test messages sent to WhatsApp 7259510983!")
