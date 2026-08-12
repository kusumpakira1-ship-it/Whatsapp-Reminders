import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 287")
print(cur.fetchone())
cur.close()
conn.close()
