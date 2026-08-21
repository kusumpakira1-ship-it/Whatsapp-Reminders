"""
Inspect sunfra_processed_data schema.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("DESCRIBE sunfra_processed_data")
cols = cursor.fetchall()
print("=== SUNFRA_PROCESSED_DATA COLUMNS ===")
for c in cols:
    print(f"  {c['Field']} ({c['Type']})")

cursor.execute("SELECT * FROM sunfra_processed_data WHERE category IN ('hen_weight', 'weight', 'birds_weight') LIMIT 10")
rows = cursor.fetchall()
print("\nSample weight rows in sunfra_processed_data:")
for r in rows:
    print(" ", r)

conn.close()

