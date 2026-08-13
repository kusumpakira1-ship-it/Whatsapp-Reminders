"""
Search for images sent by Venkat or sent in Feed groups yesterday (12 Aug 2026)
"""

import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

start_dt = datetime.datetime(2026, 8, 12, 0, 0, 0)
end_dt = datetime.datetime(2026, 8, 12, 23, 59, 59)

print("=== SEARCHING FOR VENKAT MESSAGES ON 12 AUG 2026 ===")
cur.execute("""
SELECT * FROM sunfra_raw_messages 
WHERE timestamp >= %s AND timestamp <= %s
  AND (LOWER(sender) LIKE '%%venkat%%' OR LOWER(raw_text) LIKE '%%venkat%%')
ORDER BY timestamp
""", (start_dt, end_dt))
venkat_msgs = cur.fetchall()

print(f"Venkat Messages Count: {len(venkat_msgs)}")
for v in venkat_msgs:
    print(f"[{v['timestamp']}] Sender: {v['sender']} | Text: {v['raw_text']}")

print("\n=== SEARCHING ALL MESSAGES IN FEED GROUPS ON 12 AUG 2026 ===")
cur.execute("""
SELECT * FROM sunfra_raw_messages 
WHERE timestamp >= %s AND timestamp <= %s
  AND (LOWER(sender) LIKE '%%feed%%' OR LOWER(sender) LIKE '%%accounts%%' OR LOWER(sender) LIKE '%%plant%%')
ORDER BY timestamp
""", (start_dt, end_dt))
feed_msgs = cur.fetchall()

print(f"Feed Groups Messages Count: {len(feed_msgs)}")
for f in feed_msgs:
    print(f"[{f['timestamp']}] Sender: {f['sender']} | Text: {f['raw_text']}")

# Also check backend/media folder for files created/modified yesterday
media_dir = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend\media"
if os.path.exists(media_dir):
    print("\n=== MEDIA FILES IN BACKEND/MEDIA MODIFIED ON 12 AUG 2026 ===")
    media_files = os.listdir(media_dir)
    for mf in media_files:
        fp = os.path.join(media_dir, mf)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fp))
        if mtime.date() == datetime.date(2026, 8, 12):
            print(f"[{mtime}] File: {mf} (Size: {os.path.getsize(fp)} bytes)")

cur.close()
conn.close()
