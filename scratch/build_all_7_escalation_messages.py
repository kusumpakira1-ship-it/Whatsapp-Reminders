"""
Full implementation of 7-company Escalation Report Builder
"""

import sys, os, pymysql, datetime, re, difflib
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

def build_7_escalation_sections():
    now_ist = datetime.datetime.now()
    today_date_str = now_ist.strftime("%d %b %Y")
    
    # Fetch today's raw messages
    cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
    raw_messages = cur.fetchall()
    
    # Fetch today's processed data
    cur.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = CURRENT_DATE()")
    submissions = cur.fetchall()

    # Helper function to check if an approval message exists by sender/group
    def check_approval(sender_name_target=None, group_target=None):
        approval_kws = ["approved", "approve", "reviewed", "review", "checked", "check", "accepted", "accept", "ok", "verified", "verify", "looks good", "fine", "done"]
        for m in raw_messages:
            raw_text = (m.get('raw_text') or '').lower()
            raw_sender = (m.get('sender') or '').lower()
            raw_group = (m.get('group_name') or '').lower()
            
            sender_match = False
            if sender_name_target:
                t = sender_name_target.lower()
                sender_match = (t in raw_sender)
                
            group_match = False
            if group_target:
                gt = group_target.lower()
                group_match = (gt in raw_group)
                
            if (sender_match or group_match):
                if any(akw in raw_text for akw in approval_kws):
                    return True
        return False

    # Helper function to check report submission in raw_messages or processed_data
    def check_report_submitted(report_name, group_target=None, sender_target=None):
        rep_lower = report_name.lower()
        
        # Check ProcessedData
        for p in submissions:
            p_cat = (p.get('category') or '').lower()
            p_notes = (p.get('notes') or '').lower()
            p_group = (p.get('group_name') or '').lower()
            p_sender = (p.get('sender') or '').lower()
            
            grp_ok = (not group_target or group_target.lower() in p_group)
            snd_ok = (not sender_target or sender_target.lower() in p_sender)
            
            if grp_ok and snd_ok:
                if rep_lower in p_cat or rep_lower in p_notes or any(w in p_notes for w in rep_lower.split()):
                    return True

        # Check RawMessages
        for m in raw_messages:
            raw_text = (m.get('raw_text') or '').lower()
            raw_sender = (m.get('sender') or '').lower()
            raw_group = (m.get('group_name') or '').lower()
            
            grp_ok = (not group_target or group_target.lower() in raw_group)
            snd_ok = (not sender_target or sender_target.lower() in raw_sender)
            
            if grp_ok and snd_ok:
                if rep_lower in raw_text:
                    return True
                # Check general update keywords
                if rep_lower in ['daily work update', 'work update', 'eod update']:
                    if any(w in raw_text for w in ['update', 'updates', 'work report', 'eod', 'today work']):
                        return True
        return False

    # 1. Jataayu Jewellers Reports
    j_work = check_report_submitted('daily work update', group_target='jataayu')
    j_day = check_report_submitted('day book', group_target='jataayu')
    j_sales = check_report_submitted('daily sales', group_target='jataayu')
    j_pur = check_report_submitted('daily purchases', group_target='jataayu')
    j_pnl = check_report_submitted('weekly p&l', group_target='jataayu')

    j_items = [
        ("Jataayu updates: Daily work update", j_work),
        ("Jataayu updates: Day book", j_day),
        ("Jataayu updates: Daily sales", j_sales),
        ("Jataayu updates: Daily purchases", j_pur),
        ("Jataayu Jewellers: Weekly P&L", j_pnl),
    ]

    # 2. Sunfra Hyperscale Reports
    h_work = check_report_submitted('daily work update', group_target='hyperscale')
    h_items = [
        ("Sunfra Hyperscale: Daily Work Update", h_work),
    ]

    # 3. Monthly Rental Updates
    r_work = check_report_submitted('rental updates', group_target='rental')
    r_items = [
        ("Monthly Rental: Rental updates monthly", r_work),
    ]

    # 4. Balaji Team Reports
    b_work = check_report_submitted('daily work update', group_target='balaji')
    b_appr = check_approval(sender_name_target='balaji', group_target='balaji')
    b_items = [
        ("Balaji Team: Daily work update", b_work),
        ("Balaji (Approval Task): Report Review & Approval", b_appr),
    ]

    # 5. Corporate Company (P&L) Reports
    c_day = check_report_submitted('day book', group_target='corporate')
    c_sales = check_report_submitted('daily sales', group_target='corporate')
    c_pur = check_report_submitted('daily purchases', group_target='corporate')
    c_pay = check_report_submitted('total payables', group_target='corporate')
    c_rec = check_report_submitted('total receivables', group_target='corporate')
    c_each = check_report_submitted('each sales p&l', group_target='corporate')
    c_pnl = check_report_submitted('weekly p&l', group_target='corporate')

    c_items = [
        ("Sunfra Corporate P&L: Day book", c_day),
        ("Sunfra Corporate P&L: Daily sales", c_sales),
        ("Sunfra Corporate P&L: Daily purchases", c_pur),
        ("Sunfra Corporate P&L: Total Payables", c_pay),
        ("Sunfra Corporate P&L: Total Receivables", c_rec),
        ("Sunfra Corporate P&L: Each Sales P&L", c_each),
        ("Sunfra Corporate: Weekly P&L", c_pnl),
    ]

    # 6. Sunfra Feed Tasks & Reports
    f_silo = check_report_submitted('silo', group_target='feed plant')
    f_stock = check_report_submitted('stock', group_target='raw material')
    f_stage = check_report_submitted('stage', group_target='feed')
    f_vac = check_report_submitted('vaccine')
    f_day = check_report_submitted('day book', group_target='feeds')
    f_sales = check_report_submitted('daily sales', group_target='feeds')
    f_pur = check_report_submitted('daily purchases', group_target='feeds')
    f_pay = check_report_submitted('total payables', group_target='feeds')
    f_rec = check_report_submitted('total receivables', group_target='feeds')
    f_each = check_report_submitted('each sales p&l', group_target='feeds')
    f_pnl = check_report_submitted('weekly p&l', group_target='feeds')

    feed_items = [
        ("Sunfra Feed Plant: Silo Empty and Cleaning", f_silo),
        ("Raw Material Prices & Orders: Stock/Website Updates", f_stock),
        ("Feed Changes: Feed Stage Transitions", f_stage),
        ("Vaccines: Vaccine Schedule", f_vac),
        ("Accounts - Sunfra Feeds: Day book", f_day),
        ("Accounts - Sunfra Feeds: Daily sales", f_sales),
        ("Accounts - Sunfra Feeds: Daily purchases", f_pur),
        ("Accounts - Sunfra Feeds: Total Payables", f_pay),
        ("Accounts - Sunfra Feeds: Total Receivables", f_rec),
        ("Accounts - Sunfra Feeds: Each Sales P&L", f_each),
        ("Accounts - Sunfra Feeds: Weekly P&L", f_pnl),
    ]

    # 7. Sunfra Farms Tasks & Reports
    farm_stock = check_report_submitted('stock', group_target='ordering')
    farm_rule = check_report_submitted('rule book')
    farm_gate = check_report_submitted('gate')
    farm_form = check_report_submitted('formula')
    farm_ca = check_report_submitted('ca statement', sender_target='mahalakshmi')
    farm_day = check_report_submitted('day book', sender_target='mahalakshmi')
    farm_sales = check_report_submitted('daily sales', sender_target='mahalakshmi')
    farm_pur = check_report_submitted('daily purchases', sender_target='mahalakshmi')
    farm_pay = check_report_submitted('total payables', sender_target='mahalakshmi')
    farm_rec = check_report_submitted('total receivables', sender_target='mahalakshmi')
    farm_avg = check_report_submitted('average p&l', sender_target='mahalakshmi')
    farm_each = check_report_submitted('each sales p&l', sender_target='mahalakshmi')
    farm_sum = check_report_submitted('profit & loss summary', group_target='sunfra p&l')
    farm_pnl = check_report_submitted('weekly p&l', sender_target='mahalakshmi')

    farm_items = [
        ("Raw Material Prices & Ordering: Stock/Website Updates", farm_stock),
        ("Rule Book: Rule Book Updates", farm_rule),
        ("Gate Managers: Entry Logs", farm_gate),
        ("Feed Formula: Feed Formula Updates", farm_form),
        ("Accounts Poultry: CA Statement", farm_ca),
        ("Accounts Poultry: Day book", farm_day),
        ("Accounts Poultry: Daily sales", farm_sales),
        ("Accounts Poultry: Daily purchases", farm_pur),
        ("Accounts Poultry: Total Payables", farm_pay),
        ("Accounts Poultry: Total Receivables", farm_rec),
        ("Accounts Poultry: Average P&L", farm_avg),
        ("Accounts Poultry: Each Sales P&L", farm_each),
        ("Sunfra P&L: Profit & Loss Summary", farm_sum),
        ("Accounts Poultry: Weekly P&L", farm_pnl),
    ]

    sections_config = [
        ("1️⃣ *Jataayu Jewellers Reports:*", j_items),
        ("2️⃣ *Sunfra Hyperscale Reports:*", h_items),
        ("3️⃣ *Monthly Rental Updates:*", r_items),
        ("4️⃣ *Balaji Team Reports:*", b_items),
        ("5️⃣ *Corporate Company (P&L) Reports:*", c_items),
        ("6️⃣ *Sunfra Feed Tasks & Reports:*", feed_items),
        ("7️⃣ *Sunfra Farms Tasks & Reports:*", farm_items),
    ]

    messages_930 = []
    combined_1159_lines = [f"📊 *Company-Wise Escalation Report (EOD Summary)*\n📅 *Date:* {today_date_str}\n"]

    for title, items in sections_config:
        # Sort items: Missing (False) at TOP, Submitted (True) at BOTTOM
        sorted_items = sorted(items, key=lambda x: (1 if x[1] else 0, x[0]))
        
        lines = [f"{title}"]
        for name, sub in sorted_items:
            emoji = "🟢 Submitted" if sub else "❌ Not Submitted"
            lines.append(f"• {name} - {emoji}")
            
        msg = "\n".join(lines)
        messages_930.append(msg)
        combined_1159_lines.append(msg + "\n---")

    combined_1159_text = "\n".join(combined_1159_lines)

    return messages_930, combined_1159_text

msgs_930, msg_1159 = build_7_escalation_sections()

print(f"=== GENERATED {len(msgs_930)} SEPARATE MESSAGES FOR 9:30 PM ===")
for idx, m in enumerate(msgs_930, 1):
    print(f"\n--- MESSAGE {idx} ---")
    print(m)

print("\n\n=== COMBINED EOD MESSAGE FOR 11:59 PM ===")
print(msg_1159[:800] + "\n...")

cur.close()
conn.close()
