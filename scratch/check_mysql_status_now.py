import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Testing Hostinger MySQL connection now...")
try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sunfra_unified_reminders")
    count = cursor.fetchone()[0]
    print(f"✅ MySQL Connection SUCCESSFUL! sunfra_unified_reminders has {count} rows.")
    conn.close()
except Exception as e:
    print(f"❌ MySQL Connection FAILED: {e}")
