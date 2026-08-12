"""
Find Feed Formula group JID from DB and WAHA
"""

import sys, os, pymysql, requests, json
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT * FROM sunfra_groups WHERE LOWER(group_name) LIKE '%feed%'")
groups = cur.fetchall()

print("=== FEED GROUPS IN DB ===")
for g in groups:
    print(f"Name: {g.get('group_name')} | JID: {g.get('group_jid') or g.get('group_id')}")

# Also query WAHA API directly for groups
waha_url = os.getenv("WAHA_URL", "http://localhost:3000")
waha_session = os.getenv("WAHA_SESSION", "default")
try:
    res = requests.get(f"{waha_url}/api/chats?session={waha_session}", timeout=10)
    if res.status_code == 200:
        chats = res.json()
        print("\n=== FEED GROUPS FROM WAHA CHATS ===")
        for c in chats:
            name = c.get('name', '') or c.get('id', '')
            if 'feed' in str(name).lower() or 'formula' in str(name).lower():
                print(f"Name: {name} | ID: {c.get('id')}")
except Exception as e:
    print("WAHA fetch error:", e)

cur.close()
conn.close()
