"""
Inspect sunfra_processed_data table in MySQL database.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT category FROM sunfra_processed_data")
cats = [r['category'] for r in cursor.fetchall()]
print("Categories in sunfra_processed_data:", cats)

cursor.execute("SELECT * FROM sunfra_processed_data ORDER BY id DESC LIMIT 20")
rows = cursor.fetchall()
print(f"\n=== RECENT 20 ROWS IN SUNFRA_PROCESSED_DATA ===")
for r in rows:
    print(f"[{r.get('processed_time') or r.get('created_at')}] Shed: {r.get('shead_name') or r.get('shed_name')} | Cat: {r.get('category')} | Mort: {r.get('mortality')} | Eggs: {r.get('total_eggs')} | Trays: {r.get('trays')} | Loose: {r.get('loose')} | Wt: {r.get('average_weight') or r.get('weight')}")

conn.close()

