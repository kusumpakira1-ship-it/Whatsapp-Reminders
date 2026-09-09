from database import SessionLocal
from models import RawMessage
db = SessionLocal()
raws = db.query(RawMessage).filter(RawMessage.timestamp >= '2026-09-08 00:00:00').all()
print(f"Total raw messages today: {len(raws)}")

distinct_senders = {}
for r in raws:
    s = r.sender or 'Unknown'
    grp = r.group_name or 'No Group'
    if s not in distinct_senders:
        distinct_senders[s] = []
    distinct_senders[s].append((r.timestamp.strftime('%H:%M:%S'), grp, r.raw_text[:50]))

print(f"\nAll {len(distinct_senders)} Distinct Senders active today across ALL WhatsApp groups:")
for s, msgs in sorted(distinct_senders.items()):
    print(f"• {s} ({len(msgs)} msgs)")
    for ts, grp, txt in msgs[:3]:
        print(f"    [{ts}] in [{grp}]: {repr(txt)}")

db.close()
