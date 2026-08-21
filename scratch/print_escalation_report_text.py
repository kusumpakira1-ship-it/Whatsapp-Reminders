"""
Print generated Company-Wise Escalation Report text for today/yesterday.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

from database import SessionLocal
from scheduler import setup_scheduler
import scheduler

db = SessionLocal()

# Mock send_waha_text to capture output
captured_msgs = []
def mock_send(target, text):
    captured_msgs.append((target, text))

sys.modules['waha_helper'] = mock.MagicMock()
import waha_helper
waha_helper.send_waha_text = mock_send

from scheduler import company_wise_escalation_job
company_wise_escalation_job()

print("=== CAPTURED COMPANY-WISE ESCALATION REPORT ===")
for target, text in captured_msgs:
    print(f"\n[TARGET: {target}]")
    print(text)

db.close()

