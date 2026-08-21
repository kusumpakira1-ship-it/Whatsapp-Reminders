"""
Test expanded Loading Rates and Paper Rates extraction on Aug 13 messages.
"""
import sys, os, datetime, re
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
import json
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

from database import SessionLocal
from models import RawMessage

db = SessionLocal()

aug13_start = datetime.datetime(2026, 8, 13, 0, 0, 0)
aug13_end = datetime.datetime(2026, 8, 13, 23, 59, 59)
aug12_start = datetime.datetime(2026, 8, 12, 0, 0, 0)
aug12_end = datetime.datetime(2026, 8, 12, 23, 59, 59)

today_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= aug13_start, RawMessage.timestamp <= aug13_end).all()
yesterday_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= aug12_start, RawMessage.timestamp <= aug12_end).all()

loading_map = {}
paper_map = {}

all_rate_msgs = today_msgs + yesterday_msgs

for m in all_rate_msgs:
    text = m.raw_text or ''
    t_lower = text.lower()
    if 'loading' in t_lower or 'paper' in t_lower:
        lines = text.split('\n')
        current_sec = None
        for line in lines:
            l_lower = line.strip().lower()
            if 'loading' in l_lower:
                current_sec = 'loading'
                continue
            elif 'paper' in l_lower:
                current_sec = 'paper'
                continue

            match = re.search(r'^([A-Za-z\s\(\)]+):?\s*(\d{3})(?:\s*\(([-\d]+)\))?', line.strip())
            if match and current_sec:
                mkt = match.group(1).strip().upper()
                today_val = int(match.group(2))
                diff_val = int(match.group(3)) if match.group(3) else 0
                yesterday_val = today_val - diff_val

                target = loading_map if current_sec == 'loading' else paper_map
                if mkt not in target:
                    target[mkt] = {'today': today_val, 'yesterday': yesterday_val, 'change': diff_val}

print("=== EXTRACTED LOADING RATES FOR ALL PLACES ===")
for mkt, vals in loading_map.items():
    print(f"  {mkt:<15} | Today: {vals['today']} | Yesterday: {vals['yesterday']} | Change: {vals['change']}")

print("\n=== EXTRACTED PAPER RATES FOR ALL PLACES ===")
for mkt, vals in paper_map.items():
    print(f"  {mkt:<15} | Today: {vals['today']} | Yesterday: {vals['yesterday']} | Change: {vals['change']}")

db.close()

