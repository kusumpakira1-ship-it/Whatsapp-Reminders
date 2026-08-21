"""
Immediately dispatch yesterday's Daily Farm Summary & Egg Market Analysis PDF via WAHA.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

print("1. Dispatching Daily Farm Summary text report via WAHA...")
try:
    from daily_farm_summary import send_daily_farm_summary_930pm_job
    send_daily_farm_summary_930pm_job()
    print("✅ Daily Farm Summary sent successfully!")
except Exception as e:
    print(f"❌ Error sending Daily Farm Summary: {e}")

print("\n2. Dispatching Egg Price & Market Analysis PDF via WAHA...")
try:
    from egg_market_analyzer import send_daily_egg_market_pdf_job
    send_daily_egg_market_pdf_job()
    print("✅ Egg Price & Market Analysis PDF sent successfully!")
except Exception as e:
    print(f"❌ Error sending Egg Market Analysis PDF: {e}")

