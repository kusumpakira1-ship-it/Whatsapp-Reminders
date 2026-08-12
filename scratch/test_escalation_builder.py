"""
Test script to verify 7-company escalation report builder logic
"""

import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT * FROM sunfra_unified_reminders")
reminders = cur.fetchall()

cur.execute("SELECT * FROM sunfra_tasks")
tasks = cur.fetchall()

cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
raw_messages = cur.fetchall()

cur.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = CURRENT_DATE()")
submissions = cur.fetchall()

print("=== CHECKING ALL REMINDERS & TASKS IN DATABASE TODAY ===")
print(f"Total Reminders: {len(reminders)}")
print(f"Total Tasks: {len(tasks)}")
print(f"Total Raw Messages today: {len(raw_messages)}")
print(f"Total Processed Data today: {len(submissions)}")

cur.close()
conn.close()
