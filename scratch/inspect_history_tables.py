"""
Inspect history and raw_history tables in u632391467_kusumpakira database.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

print("=== DESCRIBE history ===")
cursor.execute("DESCRIBE history")
for c in cursor.fetchall():
    print(f"  {c['Field']} ({c['Type']})")

cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 10")
print("Sample rows in history:", cursor.fetchall())

print("\n=== DESCRIBE raw_history ===")
cursor.execute("DESCRIBE raw_history")
for c in cursor.fetchall():
    print(f"  {c['Field']} ({c['Type']})")

cursor.execute("SELECT * FROM raw_history ORDER BY id DESC LIMIT 10")
print("Sample rows in raw_history:", cursor.fetchall())

conn.close()

