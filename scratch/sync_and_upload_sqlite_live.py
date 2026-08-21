"""
Seed SQLite cleanly and upload whatsapp_reminders.sqlite and database.php to Hostinger via FTP
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
import ftplib
import os

print("=== 1. SEEDING LOCAL SQLITE BACKUP FILE ===")
sqlite_file = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\whatsapp_reminders.sqlite"
conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS sunfra_unified_reminders")
cursor.execute("DROP TABLE IF EXISTS sunfra_tasks")
cursor.execute("DROP TABLE IF EXISTS sunfra_groups")

cursor.execute("""
CREATE TABLE sunfra_unified_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_name TEXT,
    person_phone TEXT,
    whatsapp_group_id TEXT,
    report_types TEXT,
    task_notes TEXT,
    trigger_time TEXT,
    frequency TEXT,
    repeat_interval TEXT,
    status TEXT,
    sub_reports_status TEXT,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE sunfra_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT,
    task_type TEXT,
    assigned_person_name TEXT,
    assigned_person_phone TEXT,
    whatsapp_group_id TEXT,
    approver_phone TEXT,
    due_time TEXT,
    frequency TEXT,
    repeat_interval TEXT,
    status TEXT,
    completion_keywords TEXT,
    completion_details TEXT,
    sub_reports_status TEXT,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE sunfra_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    whatsapp_group_id TEXT,
    created_at TEXT
)
""")

default_reminders = [
    (185, 'Mahalakshmi', '6364817749', '120363042907512705@g.us', 'CA Statement,Day book,Daily sales,Daily purchases,Total Payables,Total Receivables,Average P&L,Each Sales P&L', 'Accounts Poultry', '2026-08-19 18:00:00', 'daily', 'none', 'pending', None, '2026-08-19 00:00:00'),
    (269, 'Team', '1234567890', '120363428748481277@g.us', 'Day book,Daily sales,Daily purchases,Total Payables,Total Receivables,Each Sales P&L', 'Summary - Sunfra Feeds', '2026-08-19 18:00:00', 'daily', 'none', 'pending', None, '2026-08-19 00:00:00'),
    (295, 'Team', '1234567890', '120363425581380088@g.us', 'Day book,Daily sales,Daily purchases,Total Payables,Total Receivables,Each Sales P&L', 'Sunfra Corporate P&L', '2026-08-19 18:00:00', 'daily', 'none', 'pending', None, '2026-08-19 00:00:00'),
    (213, 'Team', '1234567890', '120363430772426306@g.us', 'Rule Book Updates', 'Rule Book', '2026-08-19 17:00:00', 'daily', 'none', 'pending', None, '2026-08-19 00:00:00'),
    (222, 'Team', '1234567890', '120363428417403024@g.us', 'Daily Work Update', 'Jataayu updates', '2026-08-19 18:00:00', 'daily', 'none', 'pending', None, '2026-08-19 00:00:00'),
    (249, 'Team', '1234567890', '120363428881117777@g.us', 'Daily work update,Day book,Daily sales,Daily purchases', 'Sunfra Hyperscale', '2026-08-19 18:00:00', 'daily', 'none', 'pending', None, '2026-08-19 00:00:00'),
    (263, 'Balaji Team', '242695733772318', '120363406924564250@g.us', 'Daily work update', 'Balaji Team', '2026-08-19 18:00:00', 'daily', 'none', 'pending', None, '2026-08-19 00:00:00'),
    (294, 'Team', '1234567890', '120363429851145929@g.us', 'Stock/Website Updates', 'Raw Material Prices & Orders', '2026-08-19 11:00:00', 'daily', 'none', 'pending', None, '2026-08-19 00:00:00')
]

default_tasks = [
    (53, 'Meeting Follow up with feed and water medicine incharge worker\'s', 'meeting', 'Team', '1234567890', '120363409299826962@g.us', '7259510983', '2026-08-19 18:00:00', 'daily', 'none', 'pending', 'done,completed', 'Follow up meeting details', None, '2026-08-19 00:00:00'),
    (63, 'Silo Empty and Cleaning', 'cleaning', 'Feed Plant Team', '1234567890', '120363429948387845@g.us', '7259510983', '2026-08-19 18:00:00', 'daily', 'none', 'pending', 'cleaned,done', 'Silo cleaning task', None, '2026-08-19 00:00:00'),
    (93, '⚠️ MONTHLY VACCINE PURCHASE REMINDER 💉', 'vaccine', 'Vaccine Team', '1234567890', '120363429948387845@g.us', '7259510983', '2026-08-19 18:00:00', 'monthly', 'none', 'pending', 'purchased,done', 'Monthly vaccine purchase', None, '2026-08-19 00:00:00'),
    (96, 'Feed Formula (Requires Approval)', 'approval', 'Team', '1234567890', '120363410607412989@g.us', '7204041105', '2026-08-19 21:30:00', 'weekly', 'none', 'pending', 'approved,send', 'Feed formula approval details', None, '2026-08-19 00:00:00')
]

default_groups = [
    (1, 'Accounts Poultry', '120363042907512705@g.us', '2026-08-19 00:00:00'),
    (2, 'Summary - Sunfra Feeds', '120363428748481277@g.us', '2026-08-19 00:00:00'),
    (3, 'Sunfra Corporate P&L', '120363425581380088@g.us', '2026-08-19 00:00:00'),
    (4, 'Rule Book', '120363430772426306@g.us', '2026-08-19 00:00:00')
]

cursor.executemany("INSERT INTO sunfra_unified_reminders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", default_reminders)
cursor.executemany("INSERT INTO sunfra_tasks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", default_tasks)
cursor.executemany("INSERT INTO sunfra_groups VALUES (?,?,?,?)", default_groups)

conn.commit()
conn.close()
print("SQLite database successfully populated!")

print("\n=== 2. UPLOADING SQLITE AND DATABASE.PHP TO HOSTINGER VIA FTP ===")
ftp_host = 'ftp.sunfragroup.com'
ftp_user = 'u632391467.kusum1'
ftp_pass = 'h3>R~fQ*z?m'

local_database_php = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\database.php'

try:
    ftp = ftplib.FTP()
    ftp.connect(ftp_host, 21, timeout=30)
    ftp.login(ftp_user, ftp_pass)
    ftp.set_pasv(True)

    upload_map = [
        ('/public_html/kusum/Whatsapp_Rem/whatsapp_reminders.sqlite', sqlite_file),
        ('/public_html/kusum/Whatsapp_Rem/frontend/whatsapp_reminders.sqlite', sqlite_file),
        ('/public_html/whatsapp_reminders.sqlite', sqlite_file),
        ('/public_html/kusum/Whatsapp_Rem/database.php', local_database_php),
        ('/public_html/kusum/Whatsapp_Rem/frontend/database.php', local_database_php),
        ('/public_html/database.php', local_database_php)
    ]

    for remote_path, local_path in upload_map:
        try:
            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)
            print(f"Uploaded {local_path} -> {remote_path}")
        except Exception as e:
            print(f"Error uploading {remote_path}: {e}")

    ftp.quit()
    print("FTP Sync Complete!")
except Exception as e:
    print(f"FTP Error: {e}")
