"""
Inspect sunfra_book_standards schema.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("DESCRIBE sunfra_book_standards")
cols = cursor.fetchall()
print("=== SUNFRA_BOOK_STANDARDS COLUMNS ===")
for c in cols:
    print(f"  {c['Field']} ({c['Type']})")

cursor.execute("SELECT * FROM sunfra_book_standards LIMIT 5")
print("\nSample rows:")
for r in cursor.fetchall():
    print(" ", r)

conn.close()

