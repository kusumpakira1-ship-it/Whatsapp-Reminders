"""
Test generating full Egg Market Analysis PDF for Aug 13 with all places.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

from database import SessionLocal
from models import RawMessage
from egg_market_analyzer import parse_market_rates_from_messages, calculate_market_analysis, generate_egg_market_pdf

db = SessionLocal()

aug13_start = datetime.datetime(2026, 8, 13, 0, 0, 0)
aug13_end = datetime.datetime(2026, 8, 13, 23, 59, 59)
aug12_start = datetime.datetime(2026, 8, 12, 0, 0, 0)
aug12_end = datetime.datetime(2026, 8, 12, 23, 59, 59)

today_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= aug13_start, RawMessage.timestamp <= aug13_end).all()
yesterday_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= aug12_start, RawMessage.timestamp <= aug12_end).all()

res = parse_market_rates_from_messages(today_msgs, yesterday_msgs)
analysis = calculate_market_analysis(res)

out_pdf = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\Egg_Price_Market_Analysis_13_Aug_2026.pdf'
pdf_path = generate_egg_market_pdf(analysis, out_pdf, "13 Aug 2026")

print(f"\n🎉 Successfully generated PDF report for ALL PLACES at:\n{pdf_path}")
print(f"File size: {os.path.getsize(pdf_path)} bytes")

db.close()

