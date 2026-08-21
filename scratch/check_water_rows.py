"""
Check for Water Monitoring rows in Hostinger MySQL right now
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
    
    print("=== CHECKING ALL WATER MONITORING ROWS IN HOSTINGER MYSQL ===")
    cursor.execute("""
        SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, created_at 
        FROM sunfra_unified_reminders 
        WHERE LOWER(COALESCE(person_name,'')) LIKE '%water%'
           OR LOWER(COALESCE(report_types,'')) LIKE '%water%'
           OR LOWER(COALESCE(task_notes,'')) LIKE '%water%'
           OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%water%'
           OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%120363409544891824%'
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    print(f"Total Water rows in DB: {len(rows)}")
    for r in rows:
        print(r)

    print("\n=== CHECKING SCRIPT INSERTING WATER ROWS IN DATABASE ===")
    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
