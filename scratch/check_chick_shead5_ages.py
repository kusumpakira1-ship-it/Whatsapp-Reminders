import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

today = datetime.date.today()

cur.execute("SELECT * FROM sunfra_flocks WHERE shed_name IN ('Chick 1', 'Shead 5')")
flocks = cur.fetchall()

for f in flocks:
    hatch = f['hatch_date']
    age = (today - hatch).days + 1
    w = (age - 1) // 7 + 1
    print(f"{f['shed_name']}: Hatch={hatch}, Today Age=Day {age} (Week {w})")

cur.close()
conn.close()
