"""
Simulate index.php verification logic on yesterday's messages
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import pymysql

try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, person_name, person_phone, whatsapp_group_id, report_types, sub_reports_status FROM sunfra_unified_reminders")
    reminders = cursor.fetchall()
    
    cursor.execute("SELECT id, sender, group_name, raw_text, timestamp FROM sunfra_raw_messages WHERE DATE(timestamp) = '2026-08-19'")
    raw_msgs = cursor.fetchall()
    
    print(f"Loaded {len(reminders)} reminders and {len(raw_msgs)} raw messages from yesterday.\n")
    
    kw_map = {
        'day book': ['day book', 'daybook', 'cash book', 'bank book'],
        'daily sales': ['daily sales', 'sales', 'sale', 'egg sales', 'sales by customer'],
        'daily purchases': ['daily purchase', 'daily purchases', 'purchase', 'purchases', 'buy', 'bought', 'purchases by vendor'],
        'total payables': ['total payables', 'total payable', 'payable', 'payables', 'due to', 'ap aging', 'payableee'],
        'total receivables': ['total receivables', 'total receivable', 'receivable', 'receivables', 'due from', 'ar aging', 'receivables........'],
        'ca statement': ['ca statement', 'ca', 'statement', 'audit', 'tally', 'balance sheet'],
        'average p&l': ['average p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss', 'horizontal profit'],
        'each sales p&l': ['each sales p&l', 'p&l', 'pl', 'p and l', 'profit', 'loss'],
        'profit & loss summary': ['profit & loss', 'p&l', 'pl', 'p and l', 'profit', 'loss'],
        'daily work update': ['daily work update', 'work update', 'update', 'done', 'completed', 'eod update', 'eod'],
        'stock': ['stock', 'website', 'website updates', 'ordering', 'update', 'updates', 'maize', 'soya', 'dorb', 'stonegrit', 'raw material']
    }
    
    for r in reminders:
        r_id, p_name, p_phone, g_id, r_types, sub_status = r
        if not r_types or 'water' in str(p_name).lower(): continue
        
        target_group_jid = (g_id or '').replace('@g.us', '').strip().lower()
        reports = [x.strip().lower() for x in r_types.split(',') if x.strip()]
        
        print(f"--------------------------------------------------")
        print(f"REMINDER ID {r_id} | Name: '{p_name}' | Group JID: '{g_id}'")
        print(f"Assigned Reports: {reports}")
        
        # Check matching raw messages
        group_raw = [m for m in raw_msgs if target_group_jid and target_group_jid in str(m[2]).lower()]
        print(f"Found {len(group_raw)} raw messages sent in group '{target_group_jid}' yesterday.")
        
        matched_reports = {}
        for rep in reports:
            rep_matched = False
            # Synonyms to check
            synonyms = [rep]
            for k, syn_list in kw_map.items():
                if k in rep:
                    synonyms.extend(syn_list)
            
            for m in group_raw:
                mtext = str(m[3]).lower()
                for syn in synonyms:
                    if syn in mtext:
                        rep_matched = True
                        print(f"  ✅ Sub-report '{rep}' MATCHED message ID {m[0]} (Text: {repr(m[3][:60])}) via keyword '{syn}'")
                        break
                if rep_matched: break
            
            if not rep_matched:
                print(f"  ❌ Sub-report '{rep}' NOT MATCHED!")
            matched_reports[rep] = "done" if rep_matched else "pending"
            
        print(f"Final Matched Status: {matched_reports}\n")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
