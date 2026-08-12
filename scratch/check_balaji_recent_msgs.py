import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

print("=== CHECKING MESSAGES IN SUNFRA AI INTERN GROUP / BALAJI RECENTLY ===\n")

cur.execute("SELECT * FROM sunfra_raw_messages WHERE sender LIKE '%9493928388%' OR sender LIKE '%balaji%' ORDER BY timestamp DESC LIMIT 20")
rows = cur.fetchall()

print(f"Found {len(rows)} messages for phone 9493928388 / Balaji in DB:")
for r in rows:
    print(f"  [{r['timestamp']}] Sender: {r['sender']} | Group: {r['group_name']} | Text: '{r['raw_text']}'")

cur.close()
conn.close()
