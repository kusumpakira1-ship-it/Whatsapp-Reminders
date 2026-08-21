"""
Parse real Mortality, Production (trays/loose), and Birds Weight from WhatsApp messages on 14 Aug 2026.
"""
import pymysql, sys, datetime, re
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

print(f"=== PARSING LIVE FARM DATA FROM WHATSAPP FOR {target_date} ===")

cursor.execute("""
    SELECT sender, group_name, raw_text, timestamp 
    FROM sunfra_raw_messages 
    WHERE (LOWER(group_name) LIKE '%%production%%' OR LOWER(group_name) LIKE '%%gowdown%%' OR LOWER(group_name) LIKE '%%supervisors%%' OR group_name LIKE '%%120363046205890693%%' OR group_name LIKE '%%120363407511560539%%' OR group_name LIKE '%%120363212822578807%%')
      AND timestamp >= %s AND timestamp <= %s 
    ORDER BY timestamp ASC
""", (start_of_day, end_of_day))
msgs = cursor.fetchall()

print(f"Total farm messages found yesterday: {len(msgs)}")

for m in msgs:
    txt = (m['raw_text'] or '').strip()
    ts = m['timestamp']
    print(f"[{ts.strftime('%H:%M:%S')}] {m['group_name']}: {txt}")

conn.close()

