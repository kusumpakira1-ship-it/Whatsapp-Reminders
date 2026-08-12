"""
Add custom reminder for Feed formula Ageemix change on Aug 15th at 11:00 AM IST
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

due_time = datetime.datetime(2026, 8, 15, 11, 0, 0)
task_name = "Feed formula Ageemix change shead 1-4 7.5kg to 5 kg"
group_id = "120363410607412989@g.us"  # Feed Formula Group JID

# 1. Add to sunfra_tasks table
cur.execute("""
INSERT INTO sunfra_tasks (
    task_name, task_type, assigned_person_name, assigned_person_phone,
    whatsapp_group_id, approver_phone, due_time, status, completion_keywords, completion_details
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
""", (
    task_name,
    "feed_change",
    "Feed Team",
    "1234567890",
    group_id,
    "917259510983,916364817749",
    due_time,
    "pending",
    "done,completed,updated,changed",
    "Feed formula Ageemix change for Sheds 1-4 from 7.5kg to 5kg"
))

# 2. Add to sunfra_custom_alarms table if exists
try:
    cur.execute("""
    INSERT INTO sunfra_custom_alarms (
        task_name, target_group, alarm_time, status, created_at
    ) VALUES (%s, %s, %s, %s, %s)
    """, (task_name, group_id, due_time, "pending", datetime.datetime.now()))
except Exception as e:
    print("Custom alarm insert note:", e)

conn.commit()
print("SUCCESS: Reminder created for 15 Aug 2026 at 11:00 AM IST!")

cur.execute("SELECT * FROM sunfra_tasks WHERE task_name LIKE '%Ageemix%'")
t = cur.fetchone()
print("\nCreated Task Record:")
print(t)

cur.close()
conn.close()
