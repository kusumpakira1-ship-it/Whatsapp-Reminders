"""
Comprehensive Audit of ALL WhatsApp report submissions for Yesterday (14 Aug 2026).
"""
import sys, os, datetime, pymysql
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

target_date = datetime.date(2026, 8, 14)
start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
end_of_day = datetime.datetime.combine(target_date, datetime.time.max)

print(f"==========================================================================")
print(f" 🔍 COMPREHENSIVE AUDIT OF ALL WHATSAPP SUBMISSIONS ON {target_date.strftime('%d %b %Y')}")
print(f"==========================================================================")

# Fetch all messages from sunfra_raw_messages
cursor.execute("""
    SELECT sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE timestamp >= %s AND timestamp <= %s 
    ORDER BY timestamp ASC
""", (start_of_day, end_of_day))
raw_msgs = cursor.fetchall()

# Fetch all messages from sunfra_whatsapp_messages
cursor.execute("""
    SELECT sender_id as sender, group_id as group_name, message_text as raw_text, timestamp 
    FROM sunfra_whatsapp_messages 
    WHERE timestamp >= %s AND timestamp <= %s 
    ORDER BY timestamp ASC
""", (start_of_day, end_of_day))
wa_msgs = cursor.fetchall()

# Group mapping
cursor.execute("SELECT name, whatsapp_group_id FROM sunfra_groups")
groups = cursor.fetchall()
jid_map = {}
for g in groups:
    if g['name'] and g['whatsapp_group_id']:
        clean_id = g['whatsapp_group_id'].replace('@g.us', '').strip()
        jid_map[clean_id] = g['name']

print(f"Total raw messages recorded yesterday: {len(raw_msgs) + len(wa_msgs)}")

company_groups = {
    'Jataayu Jewellers': ['120363428881117777', 'jataayu'],
    'Sunfra Hyperscale': ['120363428417403024', 'hyperscale'],
    'Balaji Team': ['120363406924564250', 'balaji'],
    'Corporate Company (P&L)': ['120363425581380088', 'corporate'],
    'Sunfra Feeds': ['120363429954274639', '120363429180468592', '120363429851145929', 'feeds', 'feed plant'],
    'Sunfra Farms / Accounts Poultry': ['120363042907512705', '120363430772426306', '120363221285198390', 'poultry', 'farm', 'rule book'],
    'Egg Gowdown & Sales': ['120363046205890693', 'gowdown']
}

all_combined = raw_msgs + wa_msgs

print("\n--------------------------------------------------------------------------")
print(" 📁 SUBMISSIONS BY COMPANY SECTION")
print("--------------------------------------------------------------------------")

for comp_name, keywords in company_groups.items():
    print(f"\n🏢 {comp_name.upper()}:")
    matched_list = []
    for m in all_combined:
        g = (m['group_name'] or '').lower()
        t = (m['raw_text'] or '').strip()
        s = m['sender']
        ts = m['timestamp']
        
        is_match = False
        for kw in keywords:
            if kw.lower() in g:
                is_match = True
                break
        if is_match and len(t) > 0:
            matched_list.append((ts, s, g, t))
            
    if matched_list:
        print(f"  Found {len(matched_list)} message(s) / submission(s):")
        for ts, s, g, t in matched_list:
            display_grp = jid_map.get(g.replace('@g.us', ''), g)
            print(f"    • [{ts.strftime('%H:%M:%S')}] From: {s:<30} | Group: {display_grp:<25} | Content: {t[:90]}")
    else:
        print("  ❌ NO SUBMISSIONS RECORDED YESTERDAY")

conn.close()

