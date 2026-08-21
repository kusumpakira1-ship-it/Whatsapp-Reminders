"""
Reset sub_reports_status to NULL for today in Hostinger MySQL
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
    
    print("=== RESETTING sub_reports_status TO NULL FOR TODAY ===")
    cursor.execute("UPDATE sunfra_unified_reminders SET sub_reports_status = NULL, status = 'pending'")
    conn.commit()
    print("Successfully reset all reminder sub_reports_status to NULL and status to pending for today!")

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
