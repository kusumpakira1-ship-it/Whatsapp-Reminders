"""
Inspect columns and rows of sunfra_tasks table in MySQL.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("DESCRIBE sunfra_tasks")
cols = cursor.fetchall()
print("Columns in sunfra_tasks:")
for c in cols:
    print(" ", c['Field'], c['Type'])

cursor.execute("SELECT * FROM sunfra_tasks")
rows = cursor.fetchall()
print(f"\nTotal tasks in sunfra_tasks: {len(rows)}")
for r in rows:
    print(r)

