"""
Find valid farm portal login credentials from MySQL.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

print("=== SUNFRA EMPLOYEES ===")
cursor.execute("SELECT * FROM sunfra_employees")
for r in cursor.fetchall():
    print(r)

print("\n=== USERS TABLES ===")
cursor.execute("SHOW TABLES LIKE '%user%'")
utables = cursor.fetchall()
for ut in utables:
    tname = list(ut.values())[0]
    cursor.execute(f"SELECT * FROM {tname}")
    print(f"Table {tname}:", cursor.fetchall())

conn.close()

