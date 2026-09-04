import os
import sqlite3
import sys
import glob
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

print("=== 1. CHECKING BACKEND SCHEDULER LOG FILES ===")
log_files = glob.glob(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\*.log') + glob.glob(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\*.log') + glob.glob(r'C:\Users\sunfra\.gemini\antigravity-ide\brain\97a2ac84-d91b-480e-9232-c005cd096857\*.log')

for lf in log_files:
    print(f"Log File: {lf}")
    try:
        with open(lf, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            print(f"  Total lines: {len(lines)}")
            # Search for errors or yesterday August 31
            aug31_lines = [l.strip() for l in lines if '2026-08-31' in l or '08-31' in l or 'ERROR' in l]
            print(f"  Aug 31 / Error lines count: {len(aug31_lines)}")
            for al in aug31_lines[-20:]:
                print("   ", al)
    except Exception as e:
        print("  Error reading:", e)

print("\n=== 2. CHECKING SQLITE REMINDER LOGS FOR AUGUST 31 ===")
try:
    conn = sqlite3.connect(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\whatsapp_reminders.sqlite')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Check tables in sqlite
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r['name'] for r in cursor.fetchall()]
    print("SQLite Tables:", tables)

    if 'sunfra_reminder_logs' in tables:
        cursor.execute("SELECT * FROM sunfra_reminder_logs WHERE date(executed_at) = '2026-08-31' ORDER BY executed_at DESC LIMIT 20")
        logs = cursor.fetchall()
        print(f"Found {len(logs)} reminder logs for Aug 31 in SQLite:")
        for l in logs:
            print("  ", dict(l))

    if 'sunfra_unified_reminders' in tables:
        cursor.execute("SELECT id, person_name, report_types, trigger_time, status, created_at FROM sunfra_unified_reminders WHERE date(trigger_time) = '2026-08-31'")
        rems = cursor.fetchall()
        print(f"Found {len(rems)} unified reminders triggered Aug 31 in SQLite:")
        for r in rems:
            print("  ", dict(r))

    conn.close()
except Exception as e:
    print("SQLite error:", e)

print("\n=== 3. CHECKING MYSQL DATABASE LOGS & SUBMISSIONS FOR AUG 31 ===")
try:
    import pymysql
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM sunfra_reminder_logs WHERE DATE(executed_at) = '2026-08-31' ORDER BY executed_at DESC LIMIT 25")
    mysql_logs = cursor.fetchall()
    print(f"Found {len(mysql_logs)} reminder logs for Aug 31 in Hostinger MySQL:")
    for ml in mysql_logs:
        print("  ", ml)

    cursor.execute("SELECT id, person_name, report_types, trigger_time, status FROM sunfra_unified_reminders WHERE DATE(trigger_time) = '2026-08-31'")
    mysql_rems = cursor.fetchall()
    print(f"Found {len(mysql_rems)} unified reminders on Aug 31 in Hostinger MySQL:")
    for mr in mysql_rems:
        print("  ", mr)

    conn.close()
except Exception as e:
    print("MySQL Error:", e)
