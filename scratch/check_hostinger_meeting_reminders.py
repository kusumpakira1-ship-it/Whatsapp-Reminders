import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

import mysql.connector

try:
    conn = mysql.connector.connect(
        host="145.223.17.70",
        user="u632391467_kusumpakira",
        password="Kusum@2026Bb!",
        database="u632391467_kusumpakira",
        connect_timeout=10
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM sunfra_unified_reminders")
    rows = cursor.fetchall()
    
    print(f"=== HOSTINGER MYSQL SUNFRA_UNIFIED_REMINDERS ({len(rows)} rows) ===")
    for r in rows:
        rt = str(r.get('report_types') or '').lower()
        tn = str(r.get('task_notes') or '').lower()
        if 'meeting' in rt or 'meeting' in tn or 'gate' in str(r.get('whatsapp_group_id')):
            print(f"ID: {r['id']} | Group: {r['whatsapp_group_id']} | Person: {r['person_name']} | Status: {r['status']} | Trigger: {r['trigger_time']}")
            print(f"  Report Types: {r['report_types']}")
            print(f"  Task Notes  : {r['task_notes']}")
            print("-" * 60)
            
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error querying Hostinger MySQL: {e}")
