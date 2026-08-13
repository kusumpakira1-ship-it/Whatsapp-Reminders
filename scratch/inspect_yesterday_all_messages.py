"""
Inspect all messages sent on 12 August 2026 with group names
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
SELECT m.id, m.timestamp, m.group_id, g.name as group_name, m.sender_id, m.message_text
FROM sunfra_whatsapp_messages m
LEFT JOIN sunfra_groups g ON m.group_id = g.whatsapp_group_id
WHERE m.timestamp >= %s AND m.timestamp <= %s
ORDER BY m.timestamp
""", (start_dt, end_dt))

rows = cur.fetchall()

print(f"=== ALL MESSAGES RECEIVED YESTERDAY (Total: {len(rows)}) ===")

pdf_docs = []
for r in rows:
    txt = str(r['message_text'] or '')
    gn = str(r['group_name'] or r['group_id'])
    if '.pdf' in txt.lower() or '.jpg' in txt.lower() or '.png' in txt.lower() or 'report' in txt.lower() or 'update' in txt.lower() or 'book' in txt.lower() or 'sales' in txt.lower() or 'purchase' in txt.lower() or 'p&l' in txt.lower() or 'statement' in txt.lower():
        pdf_docs.append(r)

print(f"\n=== POTENTIAL REPORT / MEDIA / PDF MESSAGES (Total: {len(pdf_docs)}) ===")
for p in pdf_docs:
    gn = p['group_name'] or p['group_id']
    print(f"[{p['timestamp']}] Group: {gn} | Sender: {p['sender_id']} | Text: {p['message_text']}")

cur.close()
conn.close()
