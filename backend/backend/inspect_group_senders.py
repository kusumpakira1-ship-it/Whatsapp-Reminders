from database import SessionLocal
from models import RawMessage
db = SessionLocal()
raws = db.query(RawMessage).all()
senders = {}
for r in raws:
    grp = r.group_name or 'No Group'
    s = str(r.sender or '')
    if grp not in senders:
        senders[grp] = set()
    senders[grp].add(s)

target_groups = ['ai', 'iot', 'olx', 'cee', 'jataayu', 'corporate', 'mudah', 'hr', 'indus', 'farm', 'feed', 'management']
for grp, s_set in senders.items():
    if any(tg in grp.lower() for tg in target_groups):
        print(f"=== Group: {grp} ({len(s_set)} senders) ===")
        for s in list(s_set)[:10]:
            print(f"  - {s}")
db.close()
