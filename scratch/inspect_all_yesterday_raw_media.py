"""
Inspect raw media messages and attachments received on 12 August 2026
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

start_dt = datetime.datetime(2026, 8, 12, 0, 0, 0)
end_dt = datetime.datetime(2026, 8, 12, 23, 59, 59)

cur.execute("""
SELECT * FROM sunfra_raw_messages
WHERE timestamp >= %s AND timestamp <= %s
  AND (raw_text LIKE '%%.pdf%%' OR raw_text LIKE '%%.jpg%%' OR raw_text LIKE '%%.png%%' OR raw_text LIKE '%%.jpeg%%' OR raw_text LIKE '%%invoices%%' OR raw_text LIKE '%%Day Book%%')
ORDER BY timestamp
""", (start_dt, end_dt))

rows = cur.fetchall()
print(f"=== RAW MESSAGES WITH PDF / IMAGES / ATTACHMENTS (Total: {len(rows)}) ===")
for r in rows:
    print(f"[{r['timestamp']}] Sender: {r['sender']} | Text: {r['raw_text']}")

cur.close()
conn.close()
