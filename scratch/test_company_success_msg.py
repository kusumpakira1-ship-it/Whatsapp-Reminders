"""
Test per-company success message generator
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

def test_per_company_generator():
    now_ist = datetime.datetime.now()
    today_date_str = now_ist.strftime("%d %b %Y")
    
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
            
            sender_match = (sender_name_target and sender_name_target.lower() in raw_sender)
            group_match = (group_target and group_target.lower() in raw_group)
                
            if (sender_match or group_match):
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
        ("Jataayu updates: Daily work update", check_report_submitted('daily work update', group_target='jataayu')),
        ("Jataayu updates: Day book", check_report_submitted('day book', group_target='jataayu')),
        ("Jataayu updates: Daily sales", check_report_submitted('daily sales', group_target='jataayu')),
        ("Jataayu updates: Daily purchases", check_report_submitted('daily purchases', group_target='jataayu')),
    ]
    h_items = [
        ("Sunfra Hyperscale: Daily Work Update", check_report_submitted('daily work update', group_target='hyperscale')),
    ]
    r_items = [
        ("Monthly Rental: Rental updates monthly", check_report_submitted('rental updates', group_target='rental')),
    ]
    b_items = [
        ("Balaji Team: Daily work update", check_report_submitted('daily work update', group_target='balaji')),
        ("Balaji (Approval Task): Report Review & Approval", check_approval(sender_name_target='balaji', group_target='balaji')),
    ]
    c_items = [
        ("Sunfra Corporate P&L: Day book", check_report_submitted('day book', group_target='corporate')),
        ("Sunfra Corporate P&L: Daily sales", check_report_submitted('daily sales', group_target='corporate')),
        ("Sunfra Corporate P&L: Daily purchases", check_report_submitted('daily purchases', group_target='corporate')),
        ("Sunfra Corporate P&L: Total Payables", check_report_submitted('total payables', group_target='corporate')),
        ("Sunfra Corporate P&L: Total Receivables", check_report_submitted('total receivables', group_target='corporate')),
        ("Sunfra Corporate P&L: Each Sales P&L", check_report_submitted('each sales p&l', group_target='corporate')),
    ]
    feed_items = [
        ("Sunfra Feed Plant: Silo Empty and Cleaning", check_report_submitted('silo', group_target='feed plant')),
        ("Raw Material Prices & Orders: Stock/Website Updates", check_report_submitted('stock', group_target='raw material')),
        ("Feed Changes: Feed Stage Transitions", check_report_submitted('stage', group_target='feed')),
        ("Vaccines: Vaccine Schedule", check_report_submitted('vaccine')),
        ("Accounts - Sunfra Feeds: Day book", check_report_submitted('day book', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Daily sales", check_report_submitted('daily sales', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Daily purchases", check_report_submitted('daily purchases', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Total Payables", check_report_submitted('total payables', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Total Receivables", check_report_submitted('total receivables', group_target='feeds')),
        ("Accounts - Sunfra Feeds: Each Sales P&L", check_report_submitted('each sales p&l', group_target='feeds')),
    ]
    farm_items = [
        ("Raw Material Prices & Ordering: Stock/Website Updates", check_report_submitted('stock', group_target='ordering')),
        ("Rule Book: Rule Book Updates", check_report_submitted('rule book')),
        ("Gate Managers: Entry Logs", check_report_submitted('gate')),
        ("Feed Formula: Feed Formula Updates", check_report_submitted('formula')),
        ("Accounts Poultry: CA Statement", check_report_submitted('ca statement', sender_target='mahalakshmi')),
        ("Accounts Poultry: Day book", check_report_submitted('day book', sender_target='mahalakshmi')),
        ("Accounts Poultry: Daily sales", check_report_submitted('daily sales', sender_target='mahalakshmi')),
        ("Accounts Poultry: Daily purchases", check_report_submitted('daily purchases', sender_target='mahalakshmi')),
        ("Accounts Poultry: Total Payables", check_report_submitted('total payables', sender_target='mahalakshmi')),
        ("Accounts Poultry: Total Receivables", check_report_submitted('total receivables', sender_target='mahalakshmi')),
        ("Accounts Poultry: Average P&L", check_report_submitted('average p&l', sender_target='mahalakshmi')),
        ("Accounts Poultry: Each Sales P&L", check_report_submitted('each sales p&l', sender_target='mahalakshmi')),
        ("Sunfra P&L: Profit & Loss Summary", check_report_submitted('profit & loss summary', group_target='sunfra p&l')),
    ]

    # For testing, let's simulate 1 company (Jataayu) as having ALL items submitted!
    j_items = [(x[0], True) for x in j_items]

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
    for title, items in sections_config:
        missing_items = [it for it in items if not it[1]]
        lines_930 = [f"{title}"]
        if missing_items:
            for name, sub in sorted(missing_items, key=lambda x: x[0]):
                lines_930.append(f"• {name} - ❌ Not Submitted")
        else:
            lines_930.append("All reports and tasks have been submitted successfully today! ✅")
        messages_930.append("\n".join(lines_930))

    return messages_930

msgs = test_per_company_generator()
print("=== PER-COMPANY SUCCESS MESSAGE TEST ===")
print("MSG 1 (Simulated 100% Submitted for Jataayu):")
print(msgs[0])

print("\nMSG 2 (With Missing Items for Hyperscale):")
print(msgs[1])

cur.close()
conn.close()
