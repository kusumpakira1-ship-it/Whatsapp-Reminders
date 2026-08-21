"""
Seed SQLite database with essential reminders and tasks schema & default active rows
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3

sqlite_paths = [
    r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\whatsapp_reminders.sqlite",
    r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\whatsapp_reminders.sqlite"
]

default_reminders = [
    (185, 'Mahalakshmi', '6364817749', '120363042907512705@g.us', 'CA Statement,Day book,Daily sales,Daily purchases,Total Payables,Total Receivables,Average P&L,Each Sales P&L', 'Accounts Poultry', '19:00:00', 'daily', 'pending', '{"CA Statement": "pending", "Day book": "pending", "Daily sales": "pending", "Daily purchases": "pending"}'),
    (269, 'Team', '1234567890', '120363428748481277@g.us', 'Day book,Daily sales,Daily purchases,Total Payables,Total Receivables,Each Sales P&L', 'Summary - Sunfra Feeds', '18:00:00', 'daily', 'pending', '{"Day book": "pending", "Daily sales": "pending"}'),
    (295, 'Team', '1234567890', '120363425581380088@g.us', 'Day book,Daily sales,Daily purchases,Total Payables,Total Receivables,Each Sales P&L', 'Sunfra Corporate P&L', '18:00:00', 'daily', 'pending', '{"Day book": "pending", "Daily sales": "pending"}'),
    (213, 'Team', '1234567890', '120363430772426306@g.us', 'Rule Book Updates', 'Rule Book', '17:00:00', 'daily', 'pending', None),
    (222, 'Team', '1234567890', '120363428417403024@g.us', 'Daily Work Update', 'Jataayu updates', '18:00:00', 'daily', 'pending', None),
    (249, 'Team', '1234567890', '120363428881117777@g.us', 'Daily work update,Day book,Daily sales,Daily purchases', 'Sunfra Hyperscale', '18:00:00', 'daily', 'pending', None),
    (263, 'Balaji Team', '242695733772318', '120363406924564250@g.us', 'Daily work update', 'Balaji Team', '18:00:00', 'daily', 'pending', None),
    (294, 'Team', '1234567890', '120363429851145929@g.us', 'Stock/Website Updates', 'Raw Material Prices & Orders', '11:00:00', 'daily', 'pending', None),
]

default_tasks = [
    (53, 'Meeting Follow up with feed and water medicine incharge worker\'s', 'meeting', 'Team', '1234567890', '120363409299826962@g.us', '7259510983', '18:00:00', 'daily', 'pending', 'done,completed', 'Follow up meeting details', None),
    (63, 'Silo Empty and Cleaning', 'cleaning', 'Feed Plant Team', '1234567890', '120363429948387845@g.us', '7259510983', '18:00:00', 'daily', 'pending', 'cleaned,done', 'Silo cleaning task', None),
    (93, '⚠️ MONTHLY VACCINE PURCHASE REMINDER 💉', 'vaccine', 'Vaccine Team', '1234567890', '120363429948387845@g.us', '7259510983', '18:00:00', 'monthly', 'pending', 'purchased,done', 'Monthly vaccine purchase', None),
    (96, 'Feed Formula (Requires Approval)', 'approval', 'Team', '1234567890', '120363410607412989@g.us', '7204041105', '21:30:00', 'weekly', 'pending', 'approved,send', 'Feed formula approval details', None)
]

for spath in sqlite_paths:
    conn = sqlite3.connect(spath)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM sunfra_unified_reminders")
    cursor.executemany("""
    INSERT INTO sunfra_unified_reminders 
    (id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status, sub_reports_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, default_reminders)

    cursor.execute("DELETE FROM sunfra_tasks")
    cursor.executemany("""
    INSERT INTO sunfra_tasks 
    (id, task_name, task_type, assigned_person_name, assigned_person_phone, whatsapp_group_id, approver_phone, due_time, frequency, status, completion_keywords, completion_details, sub_reports_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, default_tasks)

    conn.commit()
    conn.close()
    print(f"Seeded SQLite backup in {spath} with {len(default_reminders)} reminders and {len(default_tasks)} tasks!")
