import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from models import WhatsAppMessage, RawMessage
from sqlalchemy import desc

db = get_db_session()

print("=== CHECKING FOR DUPLICATE MESSAGES IN DATABASE ===")

was = db.query(WhatsAppMessage).order_by(desc(WhatsAppMessage.timestamp)).limit(2000).all()

duplicates = []
seen = {}

for w in was:
    chat = w.group_id or w.sender_id
    text = (w.message_text or '').strip()
    if not chat or not text or len(text) < 5:
        continue
    
    # Key by chat and trimmed text snippet
    key = (chat, text[:80])
    
    if key in seen:
        prev_time = seen[key]
        diff_sec = abs((w.timestamp - prev_time).total_seconds())
        if diff_sec <= 300: # Within 5 minutes
            duplicates.append({
                'chat': chat,
                'text': text[:100],
                'time1': prev_time,
                'time2': w.timestamp,
                'diff_sec': diff_sec
            })
    else:
        seen[key] = w.timestamp

with open(os.path.join(os.path.dirname(__file__), "duplicates_out.txt"), "w", encoding="utf-8") as f:
    f.write(f"Total potential duplicates found: {len(duplicates)}\n\n")
    for d in duplicates[:50]:
        f.write(f"[{d['time2']} vs {d['time1']}] Diff: {d['diff_sec']:.1f}s | Chat: {d['chat']}\n")
        f.write(f"   Text: {d['text']}\n\n")

db.close()
print("Done writing duplicates_out.txt")
