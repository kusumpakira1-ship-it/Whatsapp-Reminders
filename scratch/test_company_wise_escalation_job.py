"""
Test company_wise_escalation_job execution in backend/scheduler.py.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

from scheduler import company_wise_escalation_job

print("Running company_wise_escalation_job...")
company_wise_escalation_job()
print("Execution completed successfully!")

