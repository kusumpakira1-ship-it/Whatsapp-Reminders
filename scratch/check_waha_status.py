import pymysql
import requests

try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    print("=== LATEST 5 RAW MESSAGES ===")
    cursor.execute("SELECT id, timestamp, sender, group_name, raw_text FROM sunfra_raw_messages ORDER BY id DESC LIMIT 5")
    for r in cursor.fetchall():
        print(r)

    print("\n=== LATEST 5 WAHA EVENTS ===")
    cursor.execute("SELECT * FROM sunfra_waha_events ORDER BY id DESC LIMIT 5")
    for r in cursor.fetchall():
        print(r)

    conn.close()
except Exception as e:
    print("DB Error:", e)

# Test WAHA API if reachable locally or remotely
try:
    res = requests.get("http://localhost:3000/api/sessions", timeout=3)
    print("\nLocal WAHA sessions:", res.json())
except Exception as e:
    print("\nLocal WAHA check:", e)
