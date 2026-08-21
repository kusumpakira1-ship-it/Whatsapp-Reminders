"""
Search MySQL database for mortality, production, and birds weight tables.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
tables = [list(r.values())[0] for r in cursor.fetchall()]

print(f"=== ALL TABLES IN MYSQL DATABASE ({len(tables)}) ===")
for t in sorted(tables):
    print("  -", t)

print("\n--- CHECKING TABLES FOR MORTALITY/PRODUCTION/WEIGHT DATA ---")
target_tables = [t for t in tables if any(k in t.lower() for k in ['mortality', 'production', 'weight', 'supervisor', 'farm', 'egg', 'processed', 'data', 'bird'])]

for t in target_tables:
    cursor.execute(f"SELECT COUNT(*) as cnt FROM {t}")
    cnt = cursor.fetchone()['cnt']
    print(f"Table '{t:<35}': {cnt} rows")

conn.close()

