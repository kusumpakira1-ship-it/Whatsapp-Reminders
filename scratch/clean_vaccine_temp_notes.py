"""
Clean legacy temperature notes from vaccine column in sunfra_book_standards
"""

import sys, os, pymysql, re
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT day, week, vaccine FROM sunfra_book_standards WHERE vaccine IS NOT NULL AND vaccine != ''")
rows = cur.fetchall()

cleaned_count = 0
for r in rows:
    v = r['vaccine'].strip()
    if re.search(r'^\d+(\.\d+)?\s*c$', v.lower()) or v.lower().startswith('body'):
        cur.execute("UPDATE sunfra_book_standards SET vaccine = NULL WHERE day = %s", (r['day'],))
        cleaned_count += 1

conn.commit()
print(f"Cleaned {cleaned_count} non-vaccine temperature/body weight notes from sunfra_book_standards!")

cur.close()
conn.close()
