"""
Test fixing is_poorna_match in index.php logic
"""

import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 288")
r = cur.fetchone()

cur.execute("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = CURRENT_DATE()")
raw_messages = cur.fetchall()

print(f"=== TESTING REFINED MATCHING FOR REMINDER 288 ===")

for m in raw_messages:
    sender_full = (m['sender'] or '').lower()
    text_lower = (m['raw_text'] or '').lower()
    if 'poorna' in sender_full or 'poornima' in sender_full:
        print(f"Checking Poorna message: [{m['timestamp']}] '{m['raw_text']}'")
        approval_keywords = ["approved", "approve", "reviewed", "review", "checked", "check", "accepted", "accept", "ok", "verified", "verify", "looks good", "fine", "done"]
        has_kw = any(akw in text_lower for akw in approval_keywords)
        print(f"  Approval keyword present? {has_kw}")

cur.close()
conn.close()
