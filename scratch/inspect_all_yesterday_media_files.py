"""
Find all images and PDF files sent on 12 August 2026 across all groups
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
SELECT * FROM sunfra_whatsapp_messages 
WHERE timestamp >= %s AND timestamp <= %s 
  AND (message_type IN ('image', 'document', 'pdf', 'file') OR has_media = 1 OR text_content LIKE '%%.pdf%%' OR text_content LIKE '%%.png%%' OR text_content LIKE '%%.jpg%%')
ORDER BY timestamp
""", (start_dt, end_dt))

rows = cur.fetchall()
print(f"=== ALL MEDIA & PDF MESSAGES FROM YESTERDAY (Total: {len(rows)}) ===")
for r in rows:
    print(f"[{r['timestamp']}] Group: {r.get('group_name')} | Sender: {r.get('sender_name')} | Text: {r.get('text_content')} | Media: {r.get('media_path') or r.get('media_url')}")

cur.close()
conn.close()
