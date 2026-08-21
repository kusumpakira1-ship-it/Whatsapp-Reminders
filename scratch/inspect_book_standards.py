"""
Inspect sunfra_book_standards and sunfra_flocks in MySQL to see how book production % and book weight are calculated.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SELECT * FROM sunfra_flocks")
flocks = cursor.fetchall()
print(f"=== SUNFRA FLOCKS ({len(flocks)} rows) ===")
for f in flocks:
    print(f)

cursor.execute("DESCRIBE sunfra_book_standards")
cols = cursor.fetchall()
print("\n=== SUNFRA BOOK STANDARDS SCHEMA ===")
for c in cols:
    print(" ", c['Field'], c['Type'])

cursor.execute("SELECT * FROM sunfra_book_standards LIMIT 10")
standards = cursor.fetchall()
print(f"\n=== SUNFRA BOOK STANDARDS SAMPLE ({len(standards)} rows) ===")
for s in standards:
    print(s)

conn.close()

