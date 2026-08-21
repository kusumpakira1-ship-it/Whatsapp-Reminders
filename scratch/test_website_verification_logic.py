"""
Test exact website verification with Group JID resolution
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from datetime import datetime, date, timezone, timedelta
from database import SessionLocal
from models import RawMessage, Group
from sqlalchemy import func

IST = timezone(timedelta(hours=5, minutes=30))
target_date = date(2026, 8, 17)
start_of_day = datetime(2026, 8, 17, 0, 0, 0, tzinfo=IST)
end_of_day = datetime(2026, 8, 17, 23, 59, 59, tzinfo=IST)

db = SessionLocal()
try:
    group_rows = db.query(Group).all()
    groups_map = {}
    for g in group_rows:
        name = (g.name or '').strip().lower()
        wa_id = (g.whatsapp_group_id or '').strip().replace('@g.us', '').lower()
        if name and wa_id:
            groups_map[wa_id] = name

    raw_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day, RawMessage.timestamp <= end_of_day).all()

    kw_map = {
        'day book': ['day book', 'daybook', 'cash book', 'bank book'],
        'daily sales': ['daily sales', 'sales', 'sale', 'egg sales', 'sales by customer'],
        'daily purchases': ['daily purchase', 'daily purchases', 'purchase', 'purchases', 'buy', 'bought', 'purchases by vendor'],
        'total payables': ['total payables', 'total payable', 'payable', 'payables', 'due to', 'ap aging', 'payableee'],
        'total receivables': ['total receivables', 'total receivable', 'receivable', 'receivables', 'due from', 'ar aging', 'receivables........'],
        'ca statement': ['ca statement', 'ca', 'statement', 'audit', 'tally', 'balance sheet'],
        'average p&l': ['average p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss', 'horizontal profit'],
        'each sales p&l': ['each sales p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss']
    }

    def verify_reminder(group_name_target, report_list):
        target_group_name_lower = group_name_target.lower()
        res = {}
        for r_name in report_list:
            rep_lower = r_name.lower()
            expanded_kws = [rep_lower]
            for rkey, syns in kw_map.items():
                if rkey in rep_lower or rep_lower in rkey:
                    expanded_kws.extend(syns)

            found = False
            for m in raw_msgs:
                m_group = (m.group_name or '').lower().replace('@g.us', '')
                m_text = (m.raw_text or '').lower()

                resolved_group_name = groups_map.get(m_group, m_group)

                # Group match
                grp_ok = target_group_name_lower in resolved_group_name or resolved_group_name in target_group_name_lower
                if grp_ok:
                    for kw in expanded_kws:
                        if kw and kw in m_text:
                            found = True
                            break
                if found:
                    break

            res[r_name] = "🟢 DONE" if found else "🔴 PENDING"
        return res

    print("=== ACCOUNTS POULTRY VERIFICATION FOR YESTERDAY (AUG 17) ===")
    farms_reports = ['CA Statement', 'Day Book', 'Average P&L', 'Daily Sales', 'Daily Purchases', 'Total Payables', 'Total Receivables', 'Each Sales P&L']
    farms_res = verify_reminder('Accounts Poultry', farms_reports)
    for k, v in farms_res.items():
        print(f"  • {k}: {v}")

    print("\n=== SUNFRA CORPORATE P&L VERIFICATION FOR YESTERDAY (AUG 17) ===")
    corp_reports = ['Day Book', 'Daily Sales', 'Daily Purchases', 'Total Payables', 'Total Receivables', 'Each Sales P&L']
    corp_res = verify_reminder('Sunfra Corporate P&L', corp_reports)
    for k, v in corp_res.items():
        print(f"  • {k}: {v}")

finally:
    db.close()
