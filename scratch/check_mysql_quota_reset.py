import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Testing Hostinger MySQL connection and fetching scheduled reminders for tonight...")
try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status 
        FROM sunfra_unified_reminders 
        WHERE status != 'completed'
        ORDER BY trigger_time ASC
    """)
    reminders = cursor.fetchall()
    print(f"✅ Hostinger MySQL Connected! Total active reminders in database: {len(reminders)}")
    for r in reminders[:15]:
        print(f"  - [ID {r['id']}] Trigger: {r['trigger_time']} | Name: {r['person_name']} | Group: {r['whatsapp_group_id']} | Freq: {r['frequency']} | Status: {r['status']}")

    conn.close()
except Exception as e:
    print("❌ MySQL Connection Error:", e)
