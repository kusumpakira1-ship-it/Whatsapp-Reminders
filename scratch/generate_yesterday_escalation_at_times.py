"""
Generate Escalation Reports at 09:30 PM and 11:59 PM for 20 Aug 2026 (Yesterday)
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import pymysql
from datetime import datetime

try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    target_date_str = '2026-08-20'

    # 1. Fetch raw messages from target date
    cursor.execute("""
        SELECT id, sender, group_name, raw_text, timestamp 
        FROM sunfra_raw_messages 
        WHERE DATE(timestamp) = %s
        ORDER BY timestamp ASC
    """, (target_date_str,))
    raw_msgs = cursor.fetchall()

    # 2. Fetch reminders
    cursor.execute("""
        SELECT id, person_name, person_phone, whatsapp_group_id, report_types, sub_reports_status, trigger_time, status 
        FROM sunfra_unified_reminders
    """)
    reminders = cursor.fetchall()
    
    # 3. Fetch tasks
    cursor.execute("""
        SELECT id, task_name, task_type, assigned_person_name, assigned_person_phone, whatsapp_group_id, due_time, status 
        FROM sunfra_tasks
    """)
    tasks = cursor.fetchall()

    kw_map = {
        'day book': ['day book', 'daybook', 'cash book', 'bank book', 'day book (', 'daybook.pdf'],
        'daily sales': ['daily sales', 'sales', 'sale', 'egg sales', 'sales by customer', 'sales by customer (', 'sales.pdf'],
        'daily purchases': ['daily purchase', 'daily purchases', 'purchase', 'purchases', 'buy', 'bought', 'purchases by vendor', 'purchases by vendor (', 'purchases.pdf'],
        'total payables': ['total payables', 'total payable', 'payable', 'payables', 'due to', 'ap aging', 'payableee', 'payable.pdf', 'payables.pdf'],
        'total receivables': ['total receivables', 'total receivable', 'receivable', 'receivables', 'due from', 'ar aging', 'receivable.pdf', 'receivables.pdf'],
        'ca statement': ['ca statement', 'ca', 'statement', 'audit', 'tally', 'balance sheet', 'ca statement on', 'ca.pdf'],
        'average p&l': ['average p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss', 'horizontal profit', 'p&l.pdf'],
        'each sales p&l': ['each sales p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss', 'each sales p&l.pdf'],
        'profit & loss summary': ['profit & loss', 'p&l', 'pl', 'p and l', 'profit', 'loss', 'summary', 'p&l summary'],
        'daily work update': ['daily work update', 'work update', 'update', 'done', 'completed', 'eod update', 'eod', 'report'],
        'stock': ['stock', 'website', 'website updates', 'ordering', 'update', 'updates', 'maize', 'soya', 'dorb', 'stonegrit', 'raw material'],
        'stock/website updates': ['stock', 'website', 'website updates', 'ordering', 'update', 'updates', 'maize', 'soya', 'dorb', 'stonegrit', 'raw material']
    }

    def generate_report_at_cutoff(cutoff_time_str):
        cutoff_dt = datetime.strptime(f"{target_date_str} {cutoff_time_str}", "%Y-%m-%d %H:%M:%S")
        msgs_cutoff = [m for m in raw_msgs if m[4] <= cutoff_dt]
        
        report_lines = []
        report_lines.append(f"🚨 *Daily Escalation Report ({cutoff_time_str[:5]} IST - 20 Aug 2026)*")
        report_lines.append("The following is the update on yesterday's tasks and reports, organized by company:\n")

        corp_lines = []
        feeds_lines = []
        farms_tasks_lines = []
        farms_reports_lines = []

        # Process Reminders
        for r in reminders:
            r_id, p_name, p_phone, g_id, r_types, sub_status, trig_time, status = r
            if not r_types or 'water' in str(p_name).lower() or 'water' in str(r_types).lower() or 'water' in str(g_id).lower() or '120363409544891824' in str(g_id).lower():
                continue
            
            # Skip weekly reports unless Sunday/Monday
            if 'weekly' in str(r_types).lower() or 'weekly' in str(p_name).lower():
                continue
                
            target_group_jid = (g_id or '').replace('@g.us', '').strip().lower()
            reports = [x.strip().lower() for x in r_types.split(',') if x.strip()]
            
            group_raw = [m for m in msgs_cutoff if target_group_jid and (target_group_jid in str(m[2]).lower() or target_group_jid in str(m[1]).lower())]
            
            sub_results = {}
            for rep in reports:
                rep_matched = False
                synonyms = [rep]
                for k, syn_list in kw_map.items():
                    if k in rep:
                        synonyms.extend(syn_list)
                
                for m in group_raw:
                    mtext = str(m[3]).lower()
                    for syn in synonyms:
                        if syn in mtext:
                            rep_matched = True
                            break
                    if rep_matched: break
                sub_results[rep] = rep_matched

            all_done = all(sub_results.values())
            done_count = sum(1 for v in sub_results.values() if v)
            total_count = len(sub_results)
            
            disp_name = p_name if p_name and p_name.lower() != 'team' else (g_id.replace('@g.us', '') if g_id else 'Team')
            if '120363425581380088' in str(g_id): disp_name = "Sunfra Corporate P&L"
            elif '120363428881117777' in str(g_id): disp_name = "Sunfra Hyperscale"
            elif '120363042907512705' in str(g_id): disp_name = "Accounts Poultry"
            elif '120363428748481277' in str(g_id): disp_name = "Summary - Sunfra Feeds"
            elif '120363406924564250' in str(g_id): disp_name = "Jataayu / Production Updates"
            elif '120363429851145929' in str(g_id): disp_name = "Raw Material Prices & Orders"

            emoji = "✅" if all_done else ("🟡" if done_count > 0 else "❌")
            status_str = "Submitted" if all_done else (f"Partially Submitted ({done_count}/{total_count})" if done_count > 0 else "Not Submitted")
            
            line = f"- {emoji} *{disp_name}*: *{r_types}* — {status_str}"
            
            if "corporate" in str(g_id).lower() or "120363425581380088" in str(g_id) or "hyperscale" in str(g_id).lower() or "120363428881117777" in str(g_id):
                corp_lines.append(line)
            elif "feed" in str(g_id).lower() or "120363428748481277" in str(g_id) or "120363429851145929" in str(g_id) or "raw material" in str(disp_name).lower():
                feeds_lines.append(line)
            else:
                farms_reports_lines.append(line)

        # Process Tasks
        for t in tasks:
            t_id, t_name, t_type, a_name, a_phone, g_id, due_time, status = t
            if a_name and 'supervisor' in a_name.lower(): continue
            if t_name and ('water' in t_name.lower() or 'mac:' in t_name.lower()): continue
            if 'wednesday' in str(t_name).lower() or 'meeting' in str(t_name).lower(): continue

            is_completed = (status == 'completed')
            emoji = "✅" if is_completed else "❌"
            status_str = "Completed" if is_completed else "Not Completed"
            assignee = a_name or "Team"
            line = f"- {emoji} *{assignee}*: *{t_name}* — {status_str}"
            farms_tasks_lines.append(line)

        report_lines.append("🏢 *Corporate Company (P&L) Reports:*")
        report_lines.extend(corp_lines if corp_lines else ["- No corporate reports"])
        
        report_lines.append("\n🌾 *Sunfra Feeds Reports:*")
        report_lines.extend(feeds_lines if feeds_lines else ["- No feeds reports"])
        
        report_lines.append("\n🌾 *Sunfra Farms Tasks:*")
        report_lines.extend(farms_tasks_lines if farms_tasks_lines else ["- All tasks completed"])
        
        report_lines.append("\n📊 *Sunfra Farms Reports:*")
        report_lines.extend(farms_reports_lines if farms_reports_lines else ["- All reports submitted"])
        
        return "\n".join(report_lines)

    report_930 = generate_report_at_cutoff("21:30:00")
    report_1159 = generate_report_at_cutoff("23:59:59")
    
    with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\escalation_20aug_930.txt', 'w', encoding='utf-8') as f:
        f.write(report_930)
    with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\escalation_20aug_1159.txt', 'w', encoding='utf-8') as f:
        f.write(report_1159)

    print("Successfully generated 9:30 PM and 11:59 PM Escalation Reports for 20 Aug 2026!")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
