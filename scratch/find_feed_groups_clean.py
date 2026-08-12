import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT * FROM sunfra_groups WHERE LOWER(name) LIKE '%feed%' OR LOWER(name) LIKE '%formula%'")
rows = cur.fetchall()
print("=== SUNFRA FEED / FORMULA GROUPS IN DB ===")
for r in rows:
    print(f"Name: {r['name']} | JID: {r['whatsapp_group_id']}")

cur.close()
conn.close()
