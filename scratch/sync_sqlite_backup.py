"""
Sync SQLite backup database with all reminders, tasks, employees, and groups
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
import os

sqlite_paths = [
    r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\whatsapp_reminders.sqlite",
    r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\whatsapp_reminders.sqlite"
]

for spath in sqlite_paths:
    conn = sqlite3.connect(spath)
    cursor = conn.cursor()
    
    # Create tables if not exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sunfra_unified_reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_name TEXT,
        person_phone TEXT,
        whatsapp_group_id TEXT,
        report_types TEXT,
        task_notes TEXT,
        trigger_time TEXT,
        frequency TEXT,
        status TEXT,
        sub_reports_status TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sunfra_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        task_type TEXT,
        assigned_person_name TEXT,
        assigned_person_phone TEXT,
        whatsapp_group_id TEXT,
        approver_phone TEXT,
        due_time TEXT,
        frequency TEXT,
        status TEXT,
        completion_keywords TEXT,
        completion_details TEXT,
        sub_reports_status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sunfra_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        whatsapp_group_id TEXT
    )
    """)

    conn.commit()
    conn.close()
    print(f"Initialized SQLite schema in {spath}")
