"""
Dump all rows from sunfra_unified_reminders and sunfra_tasks in Hostinger MySQL
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
    
    print("=== DUMPING sunfra_unified_reminders ===")
    cursor.execute("SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency FROM sunfra_unified_reminders")
    for r in cursor.fetchall():
        print(r)

    print("\n=== DUMPING sunfra_tasks ===")
    cursor.execute("SELECT id, task_name, task_type, assigned_person_name, assigned_person_phone, whatsapp_group_id, due_time, frequency FROM sunfra_tasks")
    for r in cursor.fetchall():
        print(r)

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
