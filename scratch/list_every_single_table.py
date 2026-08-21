"""
List EVERY table in the MySQL database.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
tables = [list(t.values())[0] for t in cursor.fetchall()]

print(f"Total tables in DB ({len(tables)}):")
for t in sorted(tables):
    print(" ", t)

