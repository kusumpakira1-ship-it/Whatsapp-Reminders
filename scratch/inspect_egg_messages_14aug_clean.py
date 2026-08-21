"""
Generate & dispatch Egg Price & Market Analysis PDF specifically for Yesterday (14 Aug 2026).
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
from datetime import datetime, timezone, timedelta
from egg_market_analyzer import parse_market_rates_from_messages, calculate_market_analysis, generate_egg_market_pdf
from scheduler import send_waha_file

db = SessionLocal()

start_14 = datetime(2026, 8, 14, 0, 0, 0)
end_14   = datetime(2026, 8, 14, 23, 59, 59)

start_13 = datetime(2026, 8, 13, 0, 0, 0)
end_13   = datetime(2026, 8, 13, 23, 59, 59)

msgs_14 = db.query(RawMessage).filter(
    RawMessage.timestamp >= start_14,
    RawMessage.timestamp <= end_14
).order_by(RawMessage.timestamp.asc()).all()

msgs_13 = db.query(RawMessage).filter(
    RawMessage.timestamp >= start_13,
    RawMessage.timestamp <= end_13
).order_by(RawMessage.timestamp.asc()).all()

print(f"Total raw messages on 14 Aug 2026: {len(msgs_14)}")
print(f"Total raw messages on 13 Aug 2026: {len(msgs_13)}")

extracted = parse_market_rates_from_messages(msgs_14, msgs_13)
analysis = calculate_market_analysis(extracted)

os.makedirs(r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch", exist_ok=True)
pdf_path = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\Egg_Market_Analysis_14Aug2026_Final.pdf"
generate_egg_market_pdf(analysis, pdf_path, "14 Aug 2026")
print(f"\n✅ Successfully generated PDF: {pdf_path}")

target_phones = ["917975209680@c.us", "917259510983@c.us", "916364817749@c.us"]
caption = "📊 *Egg Price & Market Analysis Report*\nDate: 14 Aug 2026"

for target_phone in target_phones:
    print(f"Sending Egg Market Analysis PDF for 14 Aug 2026 to {target_phone}...")
    send_waha_file(target_phone, pdf_path, caption=caption)

print("✅ PDF dispatch for 14 Aug 2026 completed successfully!")
db.close()

