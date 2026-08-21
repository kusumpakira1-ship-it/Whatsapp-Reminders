"""
Test company_wise_escalation_job logic for 14 Aug 2026 and print why items are marked ✅ vs ❌.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import unittest.mock as mock
sys.modules['google'] = mock.MagicMock()
sys.modules['google.generativeai'] = mock.MagicMock()
sys.modules['ai_processor'] = mock.MagicMock()

from database import SessionLocal
from models import RawMessage, ProcessedData, UnifiedReminder, Employee, Group, Task
from sqlalchemy import func
import re

db = SessionLocal()

target_date = datetime.date(2026, 8, 14)
start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
end_of_day = datetime.datetime.combine(target_date, datetime.time.max)

raw_messages_today = db.query(RawMessage).filter(
    RawMessage.timestamp >= start_of_day,
    RawMessage.timestamp <= end_of_day
).all()

processed_today_all = db.query(ProcessedData).filter(
    func.date(ProcessedData.processed_time) == target_date
).all()

print(f"Total RawMessages on 14 Aug: {len(raw_messages_today)}")

def check_report_submitted(report_name, group_target=None, sender_target=None):
    rep_lower = report_name.lower()
    
    # 1. ProcessedData check
    for p in processed_today_all:
        p_cat = (p.category or '').lower()
        p_notes = (p.notes or '').lower()
        p_group = (p.group_name or '').lower()
        p_sender = (p.sender or '').lower()
        
        group_target_lower = group_target.lower() if group_target else ''
        grp_ok = not group_target or (group_target_lower in p_group) or ('rule' in group_target_lower and '120363430772426306' in p_group)
        snd_ok = (not sender_target or sender_target.lower() in p_sender)
        
        if grp_ok and snd_ok:
            if rep_lower in p_cat or rep_lower in p_notes or any(w in p_notes for w in rep_lower.split()):
                return True, f"Matched in ProcessedData: category='{p.category}', notes='{p.notes}'"

    # 2. RawMessage check with smart synonyms
    kw_map = {
        'day book': ['day book', 'daybook', 'cash book', 'bank book'],
        'daily sales': ['daily sales', 'sales', 'sale', 'egg sales'],
        'daily purchases': ['daily purchase', 'daily purchases', 'purchase', 'purchases', 'buy', 'bought'],
        'total payables': ['total payables', 'total payable', 'payable', 'payables', 'due to'],
        'total receivables': ['total receivables', 'total receivable', 'receivable', 'receivables', 'due from'],
        'ca statement': ['ca statement', 'ca', 'statement', 'audit', 'tally', 'balance sheet'],
        'average p&l': ['average p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss'],
        'each sales p&l': ['each sales p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss'],
        'profit & loss summary': ['profit & loss', 'p&l', 'pl', 'p and l', 'profit', 'loss'],
        'daily work update': ['daily work update', 'work update', 'update', 'done', 'completed']
    }
    
    search_kws = [rep_lower]
    for rkey, syns in kw_map.items():
        if rkey in rep_lower:
            search_kws.extend(syns)
            
    for m in raw_messages_today:
        raw_text = (m.raw_text or '').lower()
        raw_sender = (m.sender or '').lower()
        raw_group = (m.group_name or '').lower()
        
        group_target_lower = group_target.lower() if group_target else ''
        grp_ok = not group_target or (group_target_lower in raw_group) or ('rule' in group_target_lower and '120363430772426306' in raw_group)
        snd_ok = (not sender_target or sender_target.lower() in raw_sender)
        
        if grp_ok and snd_ok:
            for skw in search_kws:
                if skw in raw_text:
                    return True, f"Matched in RawMessage: text='{raw_text[:60]}', sender='{m.sender}', group='{m.group_name}'"

    return False, "No matching submission found"

# Test all reports listed in user prompt
items_to_test = [
    ("Jataayu Jewellers", "Daily Purchases", "Jataayu", None),
    ("Jataayu Jewellers", "Daily Sales", "Jataayu", None),
    ("Jataayu Jewellers", "Daily Work Update", "Jataayu", None),
    ("Jataayu Jewellers", "Day Book", "Jataayu", None),
    ("Sunfra Hyperscale", "Daily Work Update", "Hyperscale", None),
    ("Balaji Team", "Daily Work Update", "Balaji", None),
    ("Sunfra Corporate P&L", "Daily Purchases", "Corporate", None),
    ("Sunfra Corporate P&L", "Daily Sales", "Corporate", None),
    ("Sunfra Corporate P&L", "Day Book", "Corporate", None),
    ("Sunfra Corporate P&L", "Each Sales P&L", "Corporate", None),
    ("Sunfra Corporate P&L", "Total Payables", "Corporate", None),
    ("Sunfra Corporate P&L", "Total Receivables", "Corporate", None),
    ("Sunfra Feeds", "Daily Purchases", "Feeds", None),
    ("Sunfra Feeds", "Daily Sales", "Feeds", None),
    ("Sunfra Feeds", "Day Book", "Feeds", None),
    ("Sunfra Feeds", "Each Sales P&L", "Feeds", None),
    ("Sunfra Feeds", "Total Payables", "Feeds", None),
    ("Sunfra Feeds", "Total Receivables", "Feeds", None),
]

for comp, rep, grp, snd in items_to_test:
    status, reason = check_report_submitted(rep, grp, snd)
    icon = "✅" if status else "❌"
    print(f"[{comp}] {rep}: {icon} -> {reason}")

db.close()

