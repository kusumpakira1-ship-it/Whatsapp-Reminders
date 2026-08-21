"""
Inspect Supervisors rows in Hostinger MySQL
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
    
    print("=== SEARCHING FOR SUPERVISORS / WED MEETING ROWS IN HOSTINGER MYSQL ===")
    cursor.execute("""
        SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, created_at 
        FROM sunfra_unified_reminders 
        WHERE LOWER(COALESCE(person_name,'')) LIKE '%supervisor%'
           OR LOWER(COALESCE(task_notes,'')) LIKE '%meeting%'
           OR LOWER(COALESCE(report_types,'')) LIKE '%meeting%'
           OR LOWER(COALESCE(report_types,'')) LIKE '%wed%'
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    print(f"Total rows found: {len(rows)}")
    for r in rows:
        print(r)

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
