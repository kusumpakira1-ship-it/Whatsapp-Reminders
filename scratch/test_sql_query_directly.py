"""
Test line 1085 SQL query directly on Hostinger MySQL
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
    
    sql_1 = "SELECT * FROM sunfra_unified_reminders WHERE (LOWER(COALESCE(person_name,'')) NOT LIKE '%water%' AND LOWER(COALESCE(report_types,'')) NOT LIKE '%water%' AND LOWER(COALESCE(task_notes,'')) NOT LIKE '%water%' AND LOWER(COALESCE(whatsapp_group_id,'')) NOT LIKE '%120363409544891824%') ORDER BY trigger_time DESC"
    
    print("Executing SQL query...")
    cursor.execute(sql_1)
    rows = cursor.fetchall()
    print(f"Success! Total rows returned: {len(rows)}")

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
