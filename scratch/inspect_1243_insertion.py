"""
Inspect database rows inserted around 12:43 PM today
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
    
    print("=== UNIFIED REMINDERS CREATED TODAY (AUG 19) ===")
    cursor.execute("""
        SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, created_at 
        FROM sunfra_unified_reminders 
        WHERE DATE(created_at) = '2026-08-19' OR DATE(trigger_time) = '2026-08-19'
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    print(f"Total rows found: {len(rows)}")
    for r in rows:
        print(r)

    print("\n=== RAW MESSAGES RECEIVED AROUND 12:40 PM - 12:45 PM TODAY ===")
    cursor.execute("""
        SELECT id, group_name, sender, raw_text, timestamp 
        FROM sunfra_raw_messages 
        WHERE timestamp >= '2026-08-19 12:30:00'
        ORDER BY id DESC
    """)
    raw_rows = cursor.fetchall()
    print(f"Total raw messages found: {len(raw_rows)}")
    for m in raw_rows:
        print(m)

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
