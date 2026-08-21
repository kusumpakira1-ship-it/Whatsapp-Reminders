"""
Check Venkat's WhatsApp messages sent today (14 Aug 2026).
"""
import pymysql, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

today = datetime.date.today().strftime("%Y-%m-%d")

cursor.execute("SELECT * FROM sunfra_whatsapp_messages WHERE DATE(timestamp) = %s AND (sender_id LIKE '%%8247586860%%' OR message_id LIKE '%%8247586860%%')", (today,))
venkat_msgs = cursor.fetchall()

print(f"=== MESSAGES FROM VENKAT TODAY ({today}) ({len(venkat_msgs)} msgs) ===")
for m in venkat_msgs:
    print(f"[{m['timestamp']}] Sender: {m['sender_id']} | Text: {m['message_text']}")

cursor.execute("SELECT * FROM sunfra_whatsapp_messages WHERE DATE(timestamp) = %s AND (LOWER(message_text) LIKE '%%daybook%%' OR LOWER(message_text) LIKE '%%day book%%' OR LOWER(message_text) LIKE '%%venkat%%')", (today,))
related_msgs = cursor.fetchall()
print(f"\n=== RELATED MESSAGES TODAY ({len(related_msgs)} msgs) ===")
for m in related_msgs:
    print(f"[{m['timestamp']}] Group: {m['group_id']} | Text: {m['message_text']}")

conn.close()

