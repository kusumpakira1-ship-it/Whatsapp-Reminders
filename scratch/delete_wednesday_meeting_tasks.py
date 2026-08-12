"""
Delete auto-generated Wednesday meeting tasks (IDs 97 to 105) from Hostinger MySQL DB
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

task_ids = [97, 98, 99, 100, 101, 102, 103, 104, 105]

cur.execute("DELETE FROM sunfra_tasks WHERE id IN (%s)" % ",".join(str(i) for i in task_ids))
deleted = cur.rowcount

conn.commit()
print(f"Successfully deleted {deleted} Wednesday meeting tasks (IDs {task_ids}) from Hostinger MySQL DB!")

cur.close()
conn.close()
