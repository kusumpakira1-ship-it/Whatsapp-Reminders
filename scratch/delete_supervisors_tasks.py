"""
Delete Supervisors Wednesday meeting tasks (IDs 114, 115, 116, 117, 118) from Hostinger MySQL
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
    
    print("=== DELETING SUPERVISORS TASKS FROM HOSTINGER MYSQL ===")
    count = cursor.execute("DELETE FROM sunfra_tasks WHERE assigned_person_name = 'Supervisors' OR id IN (114, 115, 116, 117, 118)")
    conn.commit()
    print(f"Deleted {count} Supervisors meeting tasks from Hostinger MySQL!")

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
