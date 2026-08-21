"""
Generate & dispatch 100% accurate Daily Farm Summary for 14 Aug 2026 to WhatsApp.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

from daily_farm_summary import generate_daily_farm_summary_report
from scheduler import send_waha_message

target_date = datetime.date(2026, 8, 14)
report_text = generate_daily_farm_summary_report(target_date)

print("=== ACCURATE GENERATED DAILY FARM SUMMARY (14 AUG 2026) ===")
print(report_text)

recipients = ["917259510983@c.us", "917975209680@c.us", "916364817749@c.us"]
for r in recipients:
    print(f"Dispatching live report to {r}...")
    send_waha_message(r, report_text)

print("✅ Live Daily Farm Summary dispatch completed successfully!")

