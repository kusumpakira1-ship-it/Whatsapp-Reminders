"""
Inspect report submission status for Today (14 Aug 2026).
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

cursor.execute("SELECT * FROM sunfra_whatsapp_messages WHERE DATE(timestamp) = %s ORDER BY timestamp DESC", (today,))
raw_msgs = cursor.fetchall()
print(f"Total raw messages received today ({today}): {len(raw_msgs)}")

print("\n--- SAMPLE RECENT MESSAGES TODAY ---")
for m in raw_msgs[:15]:
    grp = m.get('group_name') or m.get('whatsapp_group_id') or 'DM'
    txt = (m.get('raw_text') or '')[:120].replace('\n', ' ')
    sender = m.get('sender') or m.get('person_name') or ''
    time_str = str(m.get('timestamp'))
    print(f"[{time_str}] [{grp}] {sender}: {txt}")

cursor.execute("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = %s", (today,))
proc_msgs = cursor.fetchall()
print(f"\nTotal processed data rows today: {len(proc_msgs)}")
for p in proc_msgs[:10]:
    print(" ", p.get('category'), "|", p.get('sender'), "|", (p.get('notes') or '')[:80])

conn.close()

