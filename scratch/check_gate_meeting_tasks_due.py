"""
Check if any of the 7 Gate Manager meeting tasks were scheduled for Aug 13.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
import pymysql, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, task_name, task_type, due_time, frequency, status, completion_details 
    FROM sunfra_tasks 
    WHERE whatsapp_group_id = '120363225998735559@g.us'
""")
tasks = cursor.fetchall()
print(f"Total Gate Manager Tasks in DB: {len(tasks)}")
for t in tasks:
    print(f"ID #{t['id']} | Name: {t['task_name']} | Due: {t['due_time']} | Freq: {t['frequency']} | Status: {t['status']}")

