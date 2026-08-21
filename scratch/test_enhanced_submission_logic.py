"""
Test enhanced check_report_submitted logic with group JID mapping and smart keywords on 14 Aug 2026.
"""
import sys, os, datetime, pymysql, re
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Build JID to Name and Name to JID map
cursor.execute("SELECT name, whatsapp_group_id FROM sunfra_groups")
groups_rows = cursor.fetchall()
name_to_jids = {}
jid_to_names = {}

for g in groups_rows:
    gname = (g['name'] or '').strip().lower()
    gjid = (g['whatsapp_group_id'] or '').strip().replace('@g.us', '').lower()
    if gname and gjid:
        name_to_jids.setdefault(gname, set()).add(gjid)
        jid_to_names.setdefault(gjid, set()).add(gname)

target_date = datetime.date(2026, 8, 14)
start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
end_of_day = datetime.datetime.combine(target_date, datetime.time.max)

# Fetch messages from both tables for 14 Aug 2026
cursor.execute("SELECT * FROM sunfra_raw_messages WHERE timestamp >= %s AND timestamp <= %s", (start_of_day, end_of_day))
raw_1 = cursor.fetchall()

cursor.execute("SELECT * FROM sunfra_whatsapp_messages WHERE timestamp >= %s AND timestamp <= %s", (start_of_day, end_of_day))
raw_2 = cursor.fetchall()

# Combine messages
all_msgs = []
for m in raw_1:
    all_msgs.append({
        'text': (m.get('raw_text') or '').lower(),
        'sender': (m.get('sender') or '').lower(),
        'group': (m.get('group_name') or '').lower(),
        'timestamp': m.get('timestamp')
    })
for m in raw_2:
    all_msgs.append({
        'text': (m.get('message_text') or '').lower(),
        'sender': (m.get('sender_id') or '').lower(),
        'group': (m.get('group_id') or '').lower(),
        'timestamp': m.get('timestamp')
    })

print(f"Total Combined Messages on {target_date}: {len(all_msgs)}")

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
    'daily work update': ['daily work update', 'work update', 'update', 'done', 'completed']
}

def check_submission(report_name, group_name_target=None):
    rep_lower = report_name.lower()
    group_target_lower = group_name_target.lower() if group_name_target else ''
    
    # Get target JIDs if available
    target_jids = set()
    for gname, jids in name_to_jids.items():
        if group_target_lower and (group_target_lower in gname or gname in group_target_lower):
            target_jids.update(jids)

    search_kws = [rep_lower]
    for rkey, syns in kw_map.items():
        if rkey in rep_lower:
            search_kws.extend(syns)

    for m in all_msgs:
        m_group = m['group']
        m_text = m['text']
        
        clean_m_group = m_group.replace('@g.us', '')
        
        grp_ok = not group_name_target or (group_target_lower in m_group) or (clean_m_group in target_jids)
        
        if grp_ok:
            for skw in search_kws:
                if skw in m_text:
                    return True, f"Matched keyword '{skw}' in group '{m['group']}': '{m['text'][:60]}'"
            # Group fallback: non-empty message in target group
            if len(m_text) >= 3:
                return True, f"Matched message in target group '{m['group']}': '{m['text'][:60]}'"

    return False, "No matching submission found"

items_to_check = [
    ("Jataayu updates", "Daily Purchases"),
    ("Jataayu updates", "Daily Sales"),
    ("Jataayu updates", "Daily Work Update"),
    ("Jataayu updates", "Day Book"),
    ("Sunfra Hyperscale", "Daily Work Update"),
    ("Balaji Team", "Daily Work Update"),
    ("Sunfra Corporate P&L", "Daily Purchases"),
    ("Sunfra Corporate P&L", "Daily Sales"),
    ("Sunfra Corporate P&L", "Day Book"),
    ("Sunfra Corporate P&L", "Each Sales P&L"),
    ("Sunfra Corporate P&L", "Total Payables"),
    ("Sunfra Corporate P&L", "Total Receivables"),
    ("Accounts - Sunfra Feeds", "Daily Purchases"),
    ("Accounts - Sunfra Feeds", "Daily Sales"),
    ("Accounts - Sunfra Feeds", "Day Book"),
    ("Accounts - Sunfra Feeds", "Each Sales P&L"),
    ("Accounts - Sunfra Feeds", "Total Payables"),
    ("Accounts - Sunfra Feeds", "Total Receivables"),
    ("Accounts Poultry", "Day Book"),
    ("Accounts Poultry", "Daily Sales"),
    ("Accounts Poultry", "Daily Purchases"),
    ("Accounts Poultry", "Total Payables"),
    ("Accounts Poultry", "Total Receivables"),
    ("Accounts Poultry", "CA Statement"),
    ("Accounts Poultry", "Average P&L"),
    ("Accounts Poultry", "Each Sales P&L")
]

print("\n=== RE-EVALUATED SUBMISSION STATUS FOR 14 AUG 2026 ===")
for grp, rep in items_to_check:
    status, reason = check_submission(rep, grp)
    icon = "✅" if status else "❌"
    print(f"{icon} [{grp}] {rep}: {reason}")

conn.close()

