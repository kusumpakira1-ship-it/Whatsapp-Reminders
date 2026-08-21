import pymysql
from datetime import datetime, timezone

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

    print("=== DATABASE TABLES CHECK ===")
    cursor.execute("SHOW TABLES")
    tables = [list(r.values())[0] for r in cursor.fetchall()]
    print("Tables in DB:", [t for t in tables if t.startswith('sunfra_')])

    print("\n=== LATEST 10 RAW MESSAGES ===")
    cursor.execute("SELECT id, timestamp, sender, group_name, raw_text FROM sunfra_raw_messages ORDER BY id DESC LIMIT 10")
    for r in cursor.fetchall():
        print(f"ID: {r['id']} | Time: {r['timestamp']} | Group: {r['group_name']} | Sender: {r['sender']} | Text: {r['raw_text']}")

    print("\n=== LATEST 10 WAHA EVENTS ===")
    cursor.execute("SELECT * FROM sunfra_waha_events ORDER BY id DESC LIMIT 10")
    for r in cursor.fetchall():
        print(r)

    print("\n=== SUNFRA_REMINDERS / REMINDERS TABLE CHECK ===")
    rem_table = 'sunfra_reminders' if 'sunfra_reminders' in tables else ('reminders' if 'reminders' in tables else None)
    if rem_table:
        cursor.execute(f"SELECT * FROM {rem_table} ORDER BY id DESC LIMIT 10")
        for r in cursor.fetchall():
            print(r)
    else:
        print("No reminders table found among sunfra_ tables!")

    print("\n=== CHECKING OTHER SUNFRA TABLES LATEST RECORDS ===")
    for t in tables:
        if t.startswith('sunfra_') and t not in ('sunfra_raw_messages', 'sunfra_waha_events'):
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {t}")
                cnt = cursor.fetchone()['count']
                print(f"\nTable {t} (Total count: {cnt}):")
                cursor.execute(f"SELECT * FROM {t} ORDER BY id DESC LIMIT 3")
                for r in cursor.fetchall():
                    print("  ", r)
            except Exception as ex:
                print(f"  Error reading {t}: {ex}")

    conn.close()
except Exception as e:
    print("Error:", e)
