"""
Check latest raw messages, waha events, and backend processes
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import pymysql
from datetime import datetime

try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    print("=== LATEST 10 RAW MESSAGES ===")
    cursor.execute("SELECT id, timestamp, sender, group_name, raw_text FROM sunfra_raw_messages ORDER BY id DESC LIMIT 10")
    rows = cursor.fetchall()
    for r in rows:
        print(r)
        
    print("\n=== LATEST 5 WAHA EVENTS ===")
    cursor.execute("SELECT id, timestamp, event_type FROM sunfra_waha_events ORDER BY id DESC LIMIT 5")
    rows2 = cursor.fetchall()
    for r in rows2:
        print(r)
        
    conn.close()
except Exception as e:
    print(f"Error querying DB: {e}")
