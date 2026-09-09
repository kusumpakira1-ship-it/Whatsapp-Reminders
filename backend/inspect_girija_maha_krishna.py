from database import SessionLocal
from models import RawMessage, WhatsAppMessage
from datetime import datetime, date

db = SessionLocal()
print("=== CHECKING ALL MESSAGES TODAY FOR GIRIJA, MAHALAKSHMI, KRISHNA ===\n")

people = [
    ("Girija", ["8618580633", "133522631176396", "girija"]),
    ("Mahalakshmi", ["6364817749", "184791135711366", "mahalakshmi"]),
    ("Krishna", ["9182535260", "krishna"])
]

raws = db.query(RawMessage).filter(RawMessage.timestamp >= '2026-09-08 00:00:00').all()
w_msgs = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= '2026-09-08 00:00:00').all()

for name, search_terms in people:
    print(f"==================================================")
    print(f"👤 Person: {name} (Search terms: {search_terms})")
    print(f"==================================================")
    
    # In raw messages
    matched_raws = []
    for r in raws:
        s_str = str(r.sender or "").lower()
        if any(term in s_str for term in search_terms):
            matched_raws.append(r)
            
    print(f"Found {len(matched_raws)} Raw Messages today:")
    for r in matched_raws:
        print(f"  [{r.timestamp.strftime('%H:%M:%S')}] Group: {r.group_name} | Sender: {r.sender}")
        print(f"    Text: {repr(r.raw_text)}")

    # In whatsapp_messages
    matched_w = []
    for w in w_msgs:
        s_id = str(w.sender_id or "").lower()
        if any(term in s_id for term in search_terms):
            matched_w.append(w)
    print(f"Found {len(matched_w)} WhatsApp Messages today:")
    for w in matched_w:
        print(f"  [{w.timestamp.strftime('%H:%M:%S')}] Group: {w.group_id} | Sender: {w.sender_id} | Text: {repr(w.message_text)}")
    print()

# Also let's check all messages in Indus, Sunfra Farms, and Sunfra Mudah today to see if they posted under a different LID/name
print("==================================================")
print("🔍 CHECKING ALL SENDERS IN Indus, Sunfra Farms, Sunfra Mudah TODAY")
print("==================================================")
for g_kw in ['indus', 'farms', 'mudah']:
    g_raws = [r for r in raws if r.group_name and g_kw in r.group_name.lower()]
    print(f"\nGroup matching '{g_kw}' ({len(g_raws)} msgs today):")
    for r in g_raws:
        print(f"  [{r.timestamp.strftime('%H:%M:%S')}] Group: {r.group_name} | Sender: {r.sender} | Text: {repr(r.raw_text)}")

db.close()
