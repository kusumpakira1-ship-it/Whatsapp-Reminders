"""
Update tasks 58, 59, 77 status in Hostinger MySQL to 'completed'
because proof messages were received today in Gate Manager group:
- "Today meeting with Gate manage" (08:25 AM)
- "Shade works meeting" (08:46 AM)
- "Today conduct meeting with feed godown" (08:20 AM)
"""

import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

task_ids = [58, 59, 77]

for tid in task_ids:
    cur.execute(
        "UPDATE sunfra_tasks SET status = 'completed', completion_details = 'Submitted: WhatsApp reply detected' WHERE id = %s",
        (tid,)
    )

conn.commit()
print(f"Successfully updated task IDs {task_ids} to status='completed' in Hostinger MySQL DB!")

cur.close()
conn.close()
