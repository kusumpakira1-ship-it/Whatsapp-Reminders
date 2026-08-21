"""
Test Hostinger MySQL Connection
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
    print("SUCCESS: Connected to Hostinger MySQL DB!")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sunfra_unified_reminders")
    rem_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM sunfra_tasks")
    task_count = cursor.fetchone()[0]
    print(f"Total Unified Reminders: {rem_count}")
    print(f"Total Tasks: {task_count}")
    conn.close()
except Exception as e:
    print(f"ERROR: Could not connect to Hostinger MySQL DB: {e}")
