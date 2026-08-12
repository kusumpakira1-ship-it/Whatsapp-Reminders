"""
Preview vaccine approval request and group messages for Shead 5 and Chick 1
"""

import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT * FROM sunfra_flocks WHERE shed_name IN ('Chick 1', 'Shead 5')")
flocks = cur.fetchall()

print("=== VACCINE SCHEDULE PREVIEW FOR CHICK 1 AND SHEAD 5 ===")
for f in flocks:
    hatch = f['hatch_date']
    print(f"\n🏢 {f['shed_name']} (Hatch Date: {hatch}):")
    
    for day_offset in range(1, 150):
        v_day = day_offset
        v_date = hatch + datetime.timedelta(days=day_offset - 1)
        cur.execute("SELECT * FROM sunfra_book_standards WHERE day = %s AND vaccine IS NOT NULL AND vaccine != ''", (v_day,))
        std = cur.fetchone()
        if std:
            v_text = std['vaccine']
            if not v_text.lower().startswith('body') and 'c' not in v_text.lower()[:5]:
                print(f"  • Date: {v_date.strftime('%d %b %Y')} | Age: Day {v_day:3d} (Week {std['week']:2d}) -> Vaccine: {v_text}")

cur.close()
conn.close()
