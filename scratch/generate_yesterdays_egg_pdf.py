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

IST = timezone(timedelta(hours=5, minutes=30))
db = SessionLocal()

try:
    target_dt = datetime(2026, 8, 14, tzinfo=IST)
    today_start = target_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = target_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    yesterday_start = today_start - timedelta(days=1)
    
    # Filter 14 Aug 2026 messages
    today_messages = db.query(RawMessage).filter(
        (RawMessage.sender.like('%team%') | RawMessage.group_name.like('%team%')),
        RawMessage.timestamp >= today_start.replace(tzinfo=None),
        RawMessage.timestamp <= today_end.replace(tzinfo=None)
    ).order_by(RawMessage.timestamp.asc()).all()

    # 13 Aug 2026 messages for rate comparison
    yesterday_messages = db.query(RawMessage).filter(
        (RawMessage.sender.like('%team%') | RawMessage.group_name.like('%team%')),
        RawMessage.timestamp >= yesterday_start.replace(tzinfo=None),
        RawMessage.timestamp < today_start.replace(tzinfo=None)
    ).order_by(RawMessage.timestamp.asc()).all()
    
    print(f"Found {len(today_messages)} messages for 14 Aug 2026")
    print(f"Found {len(yesterday_messages)} messages for 13 Aug 2026")
    
    extracted = parse_market_rates_from_messages(today_messages, yesterday_messages)
    analysis = calculate_market_analysis(extracted)
    
    os.makedirs(r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch", exist_ok=True)
    date_str = "14 Aug 2026"
    pdf_path = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\Egg_Market_Analysis_14Aug2026.pdf"
    
    generate_egg_market_pdf(analysis, pdf_path, date_str)
    print(f"Generated PDF: {pdf_path}")
    
    target_phones = ["917975209680@c.us", "917259510983@c.us", "916364817749@c.us"]
    caption = f"📊 *Egg Price & Market Analysis Report*\nDate: {date_str}"
    
    for target_phone in target_phones:
        print(f"Sending Egg Market Analysis PDF for 14 Aug 2026 to {target_phone}...")
        send_waha_file(target_phone, pdf_path, caption=caption)
    print("✅ Dispatch completed!")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()

