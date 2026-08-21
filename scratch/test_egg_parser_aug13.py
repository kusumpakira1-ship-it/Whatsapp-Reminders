"""
Test parse_market_rates_from_messages on Aug 13 messages.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
import json
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

from database import SessionLocal
from models import RawMessage
from egg_market_analyzer import parse_market_rates_from_messages

db = SessionLocal()

aug13_start = datetime.datetime(2026, 8, 13, 0, 0, 0)
aug13_end = datetime.datetime(2026, 8, 13, 23, 59, 59)
aug12_start = datetime.datetime(2026, 8, 12, 0, 0, 0)
aug12_end = datetime.datetime(2026, 8, 12, 23, 59, 59)

today_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= aug13_start, RawMessage.timestamp <= aug13_end).all()
yesterday_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= aug12_start, RawMessage.timestamp <= aug12_end).all()

res = parse_market_rates_from_messages(today_msgs, yesterday_msgs)

print("=== EGG PRICES TABLE EXTRACTED FOR AUG 13 ===")
print(f"{'MARKET':<15} | {'MORNING':<10} | {'AFTERNOON':<10} | {'EVENING':<10}")
print("-" * 55)
for item in res['egg_prices']:
    mkt = item['market']
    m = str(item['morning']) if item['morning'] is not None else '—'
    a = str(item['afternoon']) if item['afternoon'] is not None else '—'
    e = str(item['evening']) if item['evening'] is not None else '—'
    print(f"{mkt:<15} | {m:<10} | {a:<10} | {e:<10}")

db.close()

