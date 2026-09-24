from database import SessionLocal
from models import RawMessage
from datetime import datetime, date

db = SessionLocal()
target_groups = [
    'Sunfra Farms', 'Sunfra Feeds', 'Indus', 'Sunfra Mudah', 'Sunfra OLX CEE',
    'Payments - Sunfra Farms', 'Payments - Sunfra Feeds', 'Sales - Sunfra Feeds'
]

raws = db.query(RawMessage).filter(RawMessage.timestamp >= '2026-09-08 00:00:00').all()

print(f"=== ALL MESSAGES TODAY (2026-09-08) IN TARGET GROUPS ({len(raws)} total msgs) ===\n")

for g in target_groups:
    g_msgs = [r for r in raws if r.group_name and g.lower() in r.group_name.lower()]
    print(f"==================================================")
    print(f"🏢 GROUP: {g} ({len(g_msgs)} messages today)")
    print(f"==================================================")
    for m in g_msgs:
        print(f"  [{m.timestamp.strftime('%H:%M:%S')}] Sender: {m.sender}")
        print(f"    Body: {repr(m.raw_text[:120])}")
    print()

# Also let's inspect yesterday's messages to see how these employees normally post their login/status
yesterday_raws = db.query(RawMessage).filter(
    RawMessage.timestamp >= '2026-09-07 00:00:00',
    RawMessage.timestamp < '2026-09-08 00:00:00'
).all()

print("\n=== SAMPLE MESSAGES FROM YESTERDAY (2026-09-07) IN TARGET GROUPS ===")
for g in target_groups:
    g_msgs = [r for r in yesterday_raws if r.group_name and g.lower() in r.group_name.lower()]
    if g_msgs:
        print(f"\n--- {g} (Yesterday: {len(g_msgs)} msgs) ---")
        for m in g_msgs[:10]:
            print(f"  [{m.timestamp.strftime('%H:%M:%S')}] Sender: {m.sender} | Body: {repr(m.raw_text[:80])}")

db.close()
