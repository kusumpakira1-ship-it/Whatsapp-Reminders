"""
Inspect sunfra_groups table in MySQL to map group names to JIDs.
"""
import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SELECT * FROM sunfra_groups")
groups = cursor.fetchall()

print(f"=== SUNFRA GROUPS MAPPING ({len(groups)} rows) ===")
for g in groups:
    print(f"Name: {g['name']:<30} | JID: {g['whatsapp_group_id']}")

conn.close()

