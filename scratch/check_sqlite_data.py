"""
Check sqlite rows in whatsapp_reminders.sqlite
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

spath = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\whatsapp_reminders.sqlite"
conn = sqlite3.connect(spath)
cursor = conn.cursor()

try:
    cursor.execute("SELECT COUNT(*) FROM sunfra_unified_reminders")
    r_cnt = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM sunfra_tasks")
    t_cnt = cursor.fetchone()[0]
    print(f"SQLite Unified Reminders: {r_cnt}")
    print(f"SQLite Tasks: {t_cnt}")
finally:
    conn.close()
