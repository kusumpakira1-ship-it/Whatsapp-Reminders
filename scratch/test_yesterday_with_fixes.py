"""
Test EOD Escalation report logic against yesterday's (17 Aug 2026) data
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import json
import re
from datetime import datetime, date, timezone, timedelta
from database import SessionLocal
from models import RawMessage, WhatsAppMessage, ProcessedData, Group, UnifiedReminder, Task
from sqlalchemy import func

IST = timezone(timedelta(hours=5, minutes=30))
target_date = date(2026, 8, 17)
start_of_day = datetime(2026, 8, 17, 0, 0, 0, tzinfo=IST)
end_of_day = datetime(2026, 8, 17, 23, 59, 59, tzinfo=IST)

db = SessionLocal()
try:
    group_rows = db.query(Group).all()
    name_to_jids = {}
    for g in group_rows:
        gname = (g.name or '').strip().lower()
        gjid = (g.whatsapp_group_id or '').strip().replace('@g.us', '').lower()
        if gname and gjid:
            name_to_jids.setdefault(gname, set()).add(gjid)

    raw_msgs = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day, RawMessage.timestamp <= end_of_day).all()
    wa_msgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= start_of_day, WhatsAppMessage.timestamp <= end_of_day).all()
    proc_msgs = db.query(ProcessedData).filter(func.date(ProcessedData.processed_time) == target_date).all()
    rems = db.query(UnifiedReminder).all()
    tasks = db.query(Task).all()

    combined_msgs = []
    for m in raw_msgs:
        combined_msgs.append({'text': (m.raw_text or '').lower(), 'sender': (m.sender or '').lower(), 'group': (m.group_name or '').lower()})
    for m in wa_msgs:
        combined_msgs.append({'text': (m.message_text or '').lower(), 'sender': (m.sender_id or '').lower(), 'group': (m.group_id or '').lower()})

    kw_map = {
        'day book': ['day book', 'daybook', 'cash book', 'bank book'],
        'daily sales': ['daily sales', 'sales', 'sale', 'egg sales', 'trays'],
        'daily purchases': ['daily purchase', 'daily purchases', 'purchase', 'purchases', 'buy', 'bought', 'feed', 'kg', 'tons'],
        'total payables': ['total payables', 'total payable', 'payable', 'payables', 'due to'],
        'total receivables': ['total receivables', 'total receivable', 'receivable', 'receivables', 'due from'],
        'ca statement': ['ca statement', 'ca', 'statement', 'audit', 'tally', 'balance sheet', 'otp'],
        'average p&l': ['average p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss'],
        'each sales p&l': ['each sales p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss'],
        'profit & loss summary': ['profit & loss', 'p&l', 'pl', 'p and l', 'profit', 'loss'],
        'daily work update': ['daily work update', 'work update', 'update', 'done', 'completed'],
        'stock': ['stock', 'website', 'website updates', 'ordering', 'update', 'updates', 'maize', 'soya', 'dorb', 'stonegrit', 'raw material'],
        'website updates': ['stock', 'website', 'website updates', 'ordering', 'update', 'updates', 'maize', 'soya', 'dorb', 'stonegrit', 'raw material']
    }

    def check_report_submitted(report_name, group_target=None):
        rep_lower = report_name.lower()
        group_target_lower = group_target.lower() if group_target else ''
        
        target_jids = set()
        for gname, jids in name_to_jids.items():
            if group_target_lower and (group_target_lower in gname or gname in group_target_lower):
                target_jids.update(jids)

        for p in proc_msgs:
            p_cat = (p.category or '').lower()
            p_notes = (p.notes or '').lower()
            p_group = (p.group_name or '').lower()
            grp_ok = not group_target or (group_target_lower in p_group) or any(jid in p_group for jid in target_jids)
            if grp_ok and (rep_lower in p_cat or rep_lower in p_notes):
                return True

        search_kws = [rep_lower]
        for rkey, syns in kw_map.items():
            if rkey in rep_lower:
                search_kws.extend(syns)

        for m in combined_msgs:
            m_text = m['text']
            m_group = m['group']
            clean_group_jid = m_group.replace('@g.us', '')
            grp_ok = not group_target or (group_target_lower in m_group) or (clean_group_jid in target_jids)
            if grp_ok:
                for skw in search_kws:
                    if skw in m_text:
                        return True

        for r in rems:
            r_group = (r.whatsapp_group_id or '').lower()
            grp_ok = not group_target or (group_target_lower in r_group) or any(jid in r_group for jid in target_jids)
            if grp_ok and r.sub_reports_status:
                try:
                    sub_dict = json.loads(r.sub_reports_status)
                    if isinstance(sub_dict, dict):
                        for k, v in sub_dict.items():
                            val_str = str(v).lower()
                            if val_str in ['done', 'completed', 'submitted', 'ok', '1', 'true']:
                                k_lower = k.lower()
                                if rep_lower == k_lower or rep_lower in k_lower or k_lower in rep_lower:
                                    return True
                except Exception:
                    pass

        return False

    print("=== ACCOUNTS POULTRY STATUS FOR YESTERDAY (AUG 17) ===")
    reports_farms = ['CA Statement', 'Day Book', 'Average P&L', 'Daily Sales', 'Daily Purchases', 'Total Payables', 'Total Receivables', 'Each Sales P&L']
    for rep in reports_farms:
        status = "✅ SUBMITTED" if check_report_submitted(rep, 'Accounts Poultry') else "❌ NOT SUBMITTED"
        print(f"Accounts Poultry - {rep}: {status}")

    print("\n=== SUNFRA CORPORATE P&L STATUS FOR YESTERDAY (AUG 17) ===")
    reports_corp = ['Day Book', 'Daily Sales', 'Daily Purchases', 'Total Payables', 'Total Receivables', 'Each Sales P&L']
    for rep in reports_corp:
        status = "✅ SUBMITTED" if check_report_submitted(rep, 'Sunfra Corporate P&L') else "❌ NOT SUBMITTED"
        print(f"Sunfra Corporate P&L - {rep}: {status}")

finally:
    db.close()
