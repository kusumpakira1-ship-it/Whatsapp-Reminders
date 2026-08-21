"""
Check sunfra_employees or users tables in MySQL for login credentials.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SHOW TABLES LIKE '%user%'")
utables = cursor.fetchall()
print("User Tables:", utables)

for t in utables:
    tname = list(t.values())[0]
    cursor.execute(f"SELECT * FROM {tname}")
    rows = cursor.fetchall()
    print(f"\n--- {tname} ({len(rows)} rows) ---")
    for r in rows:
        print(r)

cursor.execute("SELECT * FROM sunfra_employees")
emp_rows = cursor.fetchall()
print(f"\n--- sunfra_employees ({len(emp_rows)} rows) ---")
for r in emp_rows[:10]:
    print(r)

