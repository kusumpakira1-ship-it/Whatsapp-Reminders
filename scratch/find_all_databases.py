"""
List all databases on MySQL server host 145.223.17.70.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SHOW DATABASES")
dbs = [list(r.values())[0] for r in cursor.fetchall()]

print("=== ALL DATABASES ON HOST ===")
for d in dbs:
    print("  -", d)

conn.close()

