"""
Inspect all WhatsApp messages, images, PDFs, and documents received yesterday (12 August 2026)
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

target_date = datetime.date(2026, 8, 12)
start_dt = datetime.datetime(2026, 8, 12, 0, 0, 0)
end_dt = datetime.datetime(2026, 8, 12, 23, 59, 59)

print(f"=== CHECKING ALL MESSAGES & MEDIA RECEIVED YESTERDAY ({target_date.strftime('%d %b %Y')}) ===")

# 1. Query sunfra_raw_messages
cur.execute("SELECT * FROM sunfra_raw_messages WHERE timestamp >= %s AND timestamp <= %s ORDER BY timestamp", (start_dt, end_dt))
raw_msgs = cur.fetchall()
print(f"\n1. Raw Messages Count: {len(raw_msgs)}")
for r in raw_msgs:
    print(f"[{r['timestamp']}] Sender: {r.get('sender')} | Text: {r.get('raw_text')} | Intent: {r.get('intent')}")

# 2. Query sunfra_processed_data
cur.execute("SELECT * FROM sunfra_processed_data WHERE processed_time >= %s AND processed_time <= %s ORDER BY processed_time", (start_dt, end_dt))
processed = cur.fetchall()
print(f"\n2. Processed Data Count: {len(processed)}")
for p in processed:
    print(f"[{p['processed_time']}] Group/Sender: {p.get('group_name')} | Category: {p.get('category')} | Item: {p.get('item_name')} | Qty: {p.get('quantity')} {p.get('unit')} | Text: {p.get('raw_text')}")

# 3. Query sunfra_whatsapp_messages
cur.execute("SELECT * FROM sunfra_whatsapp_messages WHERE timestamp >= %s AND timestamp <= %s ORDER BY timestamp", (start_dt, end_dt))
wa_msgs = cur.fetchall()
print(f"\n3. WhatsApp Messages Count: {len(wa_msgs)}")
for w in wa_msgs:
    has_media = w.get('has_media') or w.get('media_url') or w.get('media_path')
    if has_media or w.get('message_type') in ['image', 'document', 'pdf', 'file']:
        print(f"[{w['timestamp']}] Group: {w.get('group_name')} ({w.get('group_id')}) | Sender: {w.get('sender_name')} ({w.get('sender_id')}) | Type: {w.get('message_type')} | Text: {w.get('text_content')} | Media: {w.get('media_path') or w.get('media_url')}")

cur.close()
conn.close()
