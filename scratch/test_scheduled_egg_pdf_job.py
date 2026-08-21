"""
Test executing scheduled_egg_market_pdf_job.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

from scheduler import scheduled_egg_market_pdf_job

print("Running scheduled_egg_market_pdf_job...")
scheduled_egg_market_pdf_job()
print("Execution completed successfully!")

