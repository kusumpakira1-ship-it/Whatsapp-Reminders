"""
Test bold report names + emojis only (✅ and ❌) + today only filtering
"""

import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

def format_bold_item(item_tuple):
    raw_name, is_sub = item_tuple
    emoji = "✅" if is_sub else "❌"
    
    # Format name so report part is bold: 'Category: *Report Name*'
    if ":" in raw_name:
        parts = raw_name.split(":", 1)
        prefix = parts[0].strip()
        rep_name = parts[1].strip()
        formatted_line = f"• {prefix}: *{rep_name}* - {emoji}"
    else:
        formatted_line = f"• *{raw_name}* - {emoji}"
    return formatted_line

def test_clean_builder():
    now_ist = datetime.datetime.now()
    today_date_str = now_ist.strftime("%d %b %Y")
    day_of_week = now_ist.strftime("%a").lower()
    day_of_month = now_ist.day
    
    is_sunday = (day_of_week == 'sun')
    is_monday = (day_of_week == 'mon')
    is_first_of_month = (day_of_month == 1)

    cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
    raw_messages = cur.fetchall()

    cur.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = CURRENT_DATE()")
    submissions = cur.fetchall()

    def check_approval(sender_name_target=None, group_target=None):
        approval_kws = ["approved", "approve", "reviewed", "review", "checked", "check", "accepted", "accept", "ok", "verified", "verify", "looks good", "fine", "done"]
        for m in raw_messages:
            raw_text = (m.get('raw_text') or '').lower()
            raw_sender = (m.get('sender') or '').lower()
            raw_group = (m.get('group_name') or '').lower()
            snd_ok = (not sender_name_target or sender_name_target.lower() in raw_sender)
            grp_ok = (not group_target or group_target.lower() in raw_group)
            if (snd_ok and grp_ok):
                if any(akw in raw_text for akw in approval_kws):
                    return True
        return False

    def check_report_submitted(report_name, group_target=None, sender_target=None):
        rep_lower = report_name.lower()
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
        for m in raw_messages:
            raw_text = (m.get('raw_text') or '').lower()
            raw_sender = (m.get('sender') or '').lower()
            raw_group = (m.get('group_name') or '').lower()
            grp_ok = (not group_target or group_target.lower() in raw_group)
            snd_ok = (not sender_target or sender_target.lower() in raw_sender)
            if grp_ok and snd_ok:
                if rep_lower in raw_text:
                    return True
                if rep_lower in ['daily work update', 'work update', 'eod update']:
                    if any(w in raw_text for w in ['update', 'updates', 'work report', 'eod', 'today work']):
                        return True
        return False

    j_items = [
        ("Jataayu updates: Daily Work Update", check_report_submitted('daily work update', group_target='jataayu')),
        ("Jataayu updates: Day Book", check_report_submitted('day book', group_target='jataayu')),
        ("Jataayu updates: Daily Sales", check_report_submitted('daily sales', group_target='jataayu')),
        ("Jataayu updates: Daily Purchases", check_report_submitted('daily purchases', group_target='jataayu')),
    ]
    if is_sunday or is_monday:
        j_items.append(("Jataayu Jewellers: Weekly P&L", check_report_submitted('weekly p&l', group_target='jataayu')))

    h_items = [
        ("Sunfra Hyperscale: Daily Work Update", check_report_submitted('daily work update', group_target='hyperscale')),
    ]

    r_items = []
    if is_first_of_month or day_of_month <= 5:
        r_items.append(("Monthly Rental: Rental Updates Monthly", check_report_submitted('rental updates', group_target='rental')))

    b_items = [
        ("Balaji Team: Daily Work Update", check_report_submitted('daily work update', group_target='balaji')),
        ("Balaji (Approval Task): Report Review & Approval", check_approval(sender_name_target='balaji', group_target='balaji')),
    ]

    c_items = [
        ("Sunfra Corporate P&L: Day Book", check_report_submitted('day book', group_target='corporate')),
        ("Sunfra Corporate P&L: Daily Sales", check_report_submitted('daily sales', group_target='corporate')),
        ("Sunfra Corporate P&L: Daily Purchases", check_report_submitted('daily purchases', group_target='corporate')),
        ("Sunfra Corporate P&L: Total Payables", check_report_submitted('total payables', group_target='corporate')),
        ("Sunfra Corporate P&L: Total Receivables", check_report_submitted('total receivables', group_target='corporate')),
        ("Sunfra Corporate P&L: Each Sales P&L", check_report_submitted('each sales p&l', group_target='corporate')),
    ]
    if is_sunday or is_monday:
        c_items.append(("Sunfra Corporate: Weekly P&L", check_report_submitted('weekly p&l', group_target='corporate')))

    feed_items = [
        ("Sunfra Feed Plant: Silo Empty and Cleaning", check_report_submitted('silo', group_target='feed plant')),
        ("Raw Material Prices & Orders: Stock/Website Updates", check_report_submitted('stock', group_target='raw material')),
        ("Feed Changes: Feed Stage Transitions", check_report_submitted('stage', group_target='feed')),
        ("Vaccines: Vaccine Schedule", check_report_submitted('vaccine')),
        ("Accounts - Sunfra Feeds: Day Book", check_report_submitted('day book', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Daily Sales", check_report_submitted('daily sales', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Daily Purchases", check_report_submitted('daily purchases', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Total Payables", check_report_submitted('total payables', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Total Receivables", check_report_submitted('total receivables', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Each Sales P&L", check_report_submitted('each sales p&l', group_target='feeds')),
    ]
    if is_sunday or is_monday:
        feed_items.append(("Accounts - Sunfra Feeds: Weekly P&L", check_report_submitted('weekly p&l', group_target='feeds')))

    farm_items = [
        ("Raw Material Prices & Ordering: Stock/Website Updates", check_report_submitted('stock', group_target='ordering')),
        ("Rule Book: Rule Book Updates", check_report_submitted('rule book')),
        ("Gate Managers: Entry Logs", check_report_submitted('gate')),
        ("Feed Formula: Feed Formula Updates", check_report_submitted('formula')),
        ("Accounts Poultry: CA Statement", check_report_submitted('ca statement', sender_target='mahalakshmi')),
        ("Accounts Poultry: Day Book", check_report_submitted('day book', sender_target='mahalakshmi')),
        ("Accounts Poultry: Daily Sales", check_report_submitted('daily sales', sender_target='mahalakshmi')),
        ("Accounts Poultry: Daily Purchases", check_report_submitted('daily purchases', sender_target='mahalakshmi')),
        ("Accounts Poultry: Total Payables", check_report_submitted('total payables', sender_target='mahalakshmi')),
        ("Accounts Poultry: Total Receivables", check_report_submitted('total receivables', sender_target='mahalakshmi')),
        ("Accounts Poultry: Average P&L", check_report_submitted('average p&l', sender_target='mahalakshmi')),
        ("Accounts Poultry: Each Sales P&L", check_report_submitted('each sales p&l', sender_target='mahalakshmi')),
        ("Sunfra P&L: Profit & Loss Summary", check_report_submitted('profit & loss summary', group_target='sunfra p&l')),
    ]
    if is_sunday or is_monday:
        farm_items.append(("Accounts Poultry: Weekly P&L", check_report_submitted('weekly p&l', sender_target='mahalakshmi')))

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
        if not items:
            continue
            
        missing_items = [it for it in items if not it[1]]
        
        lines_930 = [f"{title}"]
        if missing_items:
            for it in sorted(missing_items, key=lambda x: x[0]):
                lines_930.append(format_bold_item(it))
        else:
            lines_930.append("All reports and tasks have been submitted successfully today! ✅")
        messages_930.append("\n".join(lines_930))

        sorted_items = sorted(items, key=lambda x: (1 if x[1] else 0, x[0]))
        lines_1159 = [f"{title}"]
        for it in sorted_items:
            lines_1159.append(format_bold_item(it))
        combined_1159_lines.append("\n".join(lines_1159) + "\n---")

    combined_1159_text = "\n".join(combined_1159_lines)
    return messages_930, combined_1159_text

msgs, combined = test_clean_builder()
print("=== CLEAN BOLD + EMOJI FORMAT TEST ===")
print("9:30 PM Message 1 (Jataayu):")
print(msgs[0])

print("\n11:59 PM Combined Message Sample:")
print(combined[:600])

cur.close()
conn.close()
