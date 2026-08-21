import sys
sys.stdout.reconfigure(encoding='utf-8')
import pymysql

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

    print("=== RAW MESSAGES TODAY (2026-08-21) ===")
    cursor.execute("""
        SELECT id, timestamp, sender, group_name, raw_text 
        FROM sunfra_raw_messages 
        WHERE DATE(timestamp) = '2026-08-21' 
        ORDER BY id DESC 
        LIMIT 25
    """)
    rows = cursor.fetchall()
    print(f"Total count today: {len(rows)} (showing up to 25)")
    for r in rows:
        text = (r['raw_text'] or '').replace('\n', ' ')
        print(f"[{r['id']}] {r['timestamp']} | Group: {r['group_name']} | Sender: {r['sender'][:25]} | Msg: {text[:50]}")

    cursor.execute("SELECT COUNT(*) as cnt FROM sunfra_raw_messages WHERE DATE(timestamp) = '2026-08-21'")
    total_today = cursor.fetchone()['cnt']
    print(f"\nTotal raw messages saved today (2026-08-21): {total_today}")

    cursor.execute("SELECT COUNT(*) as cnt FROM sunfra_raw_messages WHERE DATE(timestamp) = '2026-08-20'")
    total_yesterday = cursor.fetchone()['cnt']
    print(f"Total raw messages saved yesterday (2026-08-20): {total_yesterday}")

    print("\n=== LATEST REMINDERS TODAY ===")
    cursor.execute("""
        SELECT id, person_name, person_phone, report_types, trigger_time, status 
        FROM sunfra_unified_reminders 
        ORDER BY id DESC LIMIT 15
    """)
    for r in cursor.fetchall():
        print(r)

    print("\n=== REMINDER LOGS TODAY (2026-08-21) ===")
    cursor.execute("""
        SELECT id, reminder_id, report_types, person_name, trigger_time, executed_at, status, details 
        FROM sunfra_reminder_logs 
        WHERE DATE(executed_at) = '2026-08-21' OR DATE(trigger_time) = '2026-08-21'
        ORDER BY id DESC LIMIT 20
    """)
    logs = cursor.fetchall()
    print(f"Total logs today: {len(logs)}")
    for r in logs:
        print(r)

    conn.close()
except Exception as e:
    print("Error:", e)
