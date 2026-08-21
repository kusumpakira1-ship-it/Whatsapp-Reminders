"""
Check messages for Stock/Website Updates in Raw Material Prices & Orders group on 14 Aug 2026.
"""
import sys, os, datetime, pymysql
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db_name   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db_name, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

target_date = datetime.date(2026, 8, 14)
start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
end_of_day = datetime.datetime.combine(target_date, datetime.time.max)

print(f"=== RAW MATERIAL PRICES & ORDERS MESSAGES ON {target_date} ===")

cursor.execute("""
    SELECT sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE (LOWER(group_name) LIKE '%%raw material%%' OR group_name LIKE '%%120363429851145929%%' OR group_name LIKE '%%120363421181996594%%')
      AND timestamp >= %s AND timestamp <= %s 
    ORDER BY timestamp ASC
""", (start_of_day, end_of_day))
raw_msgs = cursor.fetchall()
for m in raw_msgs:
    print(f"[{m['timestamp']}] From: {m['sender']} | Text: '{m['raw_text']}'")

cursor.execute("""
    SELECT sender_id, group_id, message_text, timestamp 
    FROM sunfra_whatsapp_messages 
    WHERE (group_id LIKE '%%120363429851145929%%' OR group_id LIKE '%%120363421181996594%%')
      AND timestamp >= %s AND timestamp <= %s 
    ORDER BY timestamp ASC
""", (start_of_day, end_of_day))
wa_msgs = cursor.fetchall()
for m in wa_msgs:
    print(f"[{m['timestamp']}] SenderID: {m['sender_id']} | Text: '{m['message_text']}'")

conn.close()

