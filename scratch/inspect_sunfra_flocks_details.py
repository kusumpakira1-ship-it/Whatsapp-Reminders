"""
Inspect sunfra_flocks in MySQL and print running weeks and live birds.
"""
import pymysql, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SELECT * FROM sunfra_flocks")
rows = cursor.fetchall()

print("=== SUNFRA FLOCKS TABLE IN MYSQL DB ===")
print(f"{'SHED NAME':<12} | {'AGE (DAYS)':<10} | {'AGE (WEEKS)':<11} | {'LIVE BIRDS':<10} | {'BATCH ID':<10} | {'STATUS':<8}")
print("-" * 75)
for r in rows:
    print(f"{r['shed_name']:<12} | {r['running_days']:<10} | {r['running_weeks']:<11} | {r['live_birds']:<10} | {str(r['batch_id']):<10} | {r['status']:<8}")

conn.close()

