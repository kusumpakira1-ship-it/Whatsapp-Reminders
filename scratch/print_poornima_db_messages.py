import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE() AND (group_name LIKE '%AIoT%' OR sender LIKE '%7204484516%' OR sender LIKE '%Poorna%')")
rows = cur.fetchall()

print(f"=== MESSAGES FOUND IN DATABASE TODAY ({len(rows)} messages) ===")
for r in rows:
    print(f"  [{r['timestamp']}] Sender: {r['sender']} | Group: {r['group_name']} | Message Text: '{r['raw_text']}'")

cur.close()
conn.close()
