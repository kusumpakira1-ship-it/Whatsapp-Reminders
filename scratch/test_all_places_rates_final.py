"""
Refine Loading Rates and Paper Rates extraction for ALL PLACES with clean filtering.
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
from egg_market_analyzer import parse_market_rates_from_messages

db = SessionLocal()

aug13_start = datetime.datetime(2026, 8, 13, 0, 0, 0)
aug13_end = datetime.datetime(2026, 8, 13, 23, 59, 59)
aug12_start = datetime.datetime(2026, 8, 12, 0, 0, 0)
aug12_end = datetime.datetime(2026, 8, 12, 23, 59, 59)

today_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= aug13_start, RawMessage.timestamp <= aug13_end).all()
yesterday_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= aug12_start, RawMessage.timestamp <= aug12_end).all()

res = parse_market_rates_from_messages(today_msgs, yesterday_msgs)

# Update backend/egg_market_analyzer.py logic in memory to test
def parse_all_places_market_rates(today_msgs, yesterday_msgs):
    res = parse_market_rates_from_messages(today_msgs, yesterday_msgs)
    
    # 1. Parse all explicit Loading & Paper rates
    loading_map = {}
    paper_map = {}
    
    ignore_words = ['NEXT', 'MONDAY', 'TRADE', 'CHAIRMAN', 'NECC', 'ZONE', 'INFORMATION', 'CULL', 'NOTICE', 'PLEASE', 'FOR', 'REGARDS', 'SUB']

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
                    if any(w in mkt for w in ignore_words) or len(mkt) > 20:
                        continue
                    today_val = int(match.group(2))
                    diff_val = int(match.group(3)) if match.group(3) else 0
                    yesterday_val = today_val - diff_val

                    target = loading_map if current_sec == 'loading' else paper_map
                    if mkt not in target:
                        target[mkt] = {'today': today_val, 'yesterday': yesterday_val, 'change': diff_val}

    # 2. Ensure ALL markets present in egg_prices are ALSO populated in Loading Rates & Paper Rates
    for item in res['egg_prices']:
        mkt = item['market']
        if any(w in mkt for w in ignore_words) or len(mkt) > 20:
            continue
        latest_val = item['evening'] or item['afternoon'] or item['morning']
        if latest_val:
            if mkt not in loading_map:
                loading_map[mkt] = {'today': latest_val, 'yesterday': latest_val, 'change': 0}
            if mkt not in paper_map:
                paper_map[mkt] = {'today': latest_val, 'yesterday': latest_val, 'change': 0}

    # Format lists
    loading_rates_list = []
    for mkt, vals in loading_map.items():
        loading_rates_list.append({"market": mkt, "yesterday": vals['yesterday'], "today": vals['today'], "change": vals['change']})

    paper_rates_list = []
    for mkt, vals in paper_map.items():
        paper_rates_list.append({"market": mkt, "yesterday": vals['yesterday'], "today": vals['today'], "change": vals['change']})

    res['loading_rates'] = loading_rates_list
    res['paper_rates'] = paper_rates_list
    return res

res_all = parse_all_places_market_rates(today_msgs, yesterday_msgs)

print(f"=== ALL PLACES LOADING RATES ({len(res_all['loading_rates'])} markets) ===")
for item in res_all['loading_rates']:
    print(f"  {item['market']:<20} | Yesterday: {item['yesterday']:<5} | Today: {item['today']:<5} | Change: {item['change']}")

print(f"\n=== ALL PLACES PAPER RATES ({len(res_all['paper_rates'])} markets) ===")
for item in res_all['paper_rates']:
    print(f"  {item['market']:<20} | Yesterday: {item['yesterday']:<5} | Today: {item['today']:<5} | Change: {item['change']}")

db.close()

