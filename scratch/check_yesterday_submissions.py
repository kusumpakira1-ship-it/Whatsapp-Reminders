"""
Check yesterday's (2026-08-19) WhatsApp messages and sub-report matching logic
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
    
    print("=== 1. RAW MESSAGES RECEIVED YESTERDAY (2026-08-19) ===")
    cursor.execute("""
        SELECT id, sender, group_name, raw_text, timestamp 
        FROM sunfra_raw_messages 
        WHERE DATE(timestamp) = '2026-08-19'
        ORDER BY timestamp DESC
    """)
    raw_msgs = cursor.fetchall()
    print(f"Total raw messages received yesterday: {len(raw_msgs)}")
    for m in raw_msgs[:20]:
        print(f"ID: {m[0]} | Group: '{m[2]}' | Sender: '{m[1]}' | Text: {repr(m[3][:100])} | Time: {m[4]}")

    print("\n=== 2. PROCESSED DATA RECORDS SAVED YESTERDAY (2026-08-19) ===")
    cursor.execute("""
        SELECT id, category, group_name, source_type, notes, processed_time 
        FROM sunfra_processed_data 
        WHERE DATE(processed_time) = '2026-08-19'
        ORDER BY processed_time DESC
    """)
    proc_msgs = cursor.fetchall()
    print(f"Total processed data records saved yesterday: {len(proc_msgs)}")
    for p in proc_msgs[:20]:
        print(f"ID: {p[0]} | Cat: '{p[1]}' | Group: '{p[2]}' | Source: '{p[3]}' | Notes: {repr(p[4][:80])} | Time: {p[5]}")

    print("\n=== 3. UNIFIED REMINDERS ON YESTERDAY (2026-08-19) ===")
    cursor.execute("""
        SELECT id, person_name, person_phone, whatsapp_group_id, report_types, sub_reports_status, trigger_time, status 
        FROM sunfra_unified_reminders 
        ORDER BY id DESC
    """)
    rems = cursor.fetchall()
    print(f"Total reminders in DB: {len(rems)}")
    for r in rems:
        print(f"ID: {r[0]} | Name: '{r[1]}' | GroupID: '{r[3]}' | Reports: '{r[4]}' | SubStatus: {r[5]} | Status: '{r[7]}'")

    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")
