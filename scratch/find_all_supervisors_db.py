"""
Search all tables in Hostinger MySQL for 'Supervisors' or 'Meeting conducted'
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
    
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"All tables in Hostinger MySQL: {tables}")

    for t in tables:
        try:
            cursor.execute(f"SELECT * FROM `{t}` WHERE LOWER(CAST(CONCAT_WS(' ', person_name, task_notes, report_types) AS CHAR)) LIKE '%supervisor%' OR LOWER(CAST(CONCAT_WS(' ', person_name, task_notes, report_types) AS CHAR)) LIKE '%meeting%'")
            rows = cursor.fetchall()
            if rows:
                print(f"\nFOUND MATCHES IN TABLE `{t}`: ({len(rows)} rows)")
                for r in rows[:10]:
                    print(r)
        except Exception as te:
            pass

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
