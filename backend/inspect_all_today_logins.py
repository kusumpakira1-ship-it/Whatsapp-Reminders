from database import SessionLocal
from models import RawMessage
db = SessionLocal()
raws = db.query(RawMessage).filter(RawMessage.timestamp >= '2026-09-08 00:00:00').all()
print(f"Total Raw Messages Today: {len(raws)}")
log_msgs = [r for r in raws if any(kw in (r.raw_text or '').lower() for kw in ['login', 'log in', 'logout', 'log out'])]
print(f"Login/Logout Messages Today: {len(log_msgs)}\n")
for r in log_msgs:
    print(f"[{r.timestamp.strftime('%H:%M:%S')}] Group: {r.group_name} | Sender: {r.sender} | Text: '{r.raw_text}'")
db.close()
