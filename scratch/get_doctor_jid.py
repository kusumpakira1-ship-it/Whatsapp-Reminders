import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage, Group

db = SessionLocal()
msgs = db.query(RawMessage).filter(RawMessage.group_name.like('%Doctor%')).all()
print("RawMessage matches for Doctor:")
for m in msgs:
    print("  GRP:", m.group_name, "| Sender:", m.sender)

# Check Group table
grp = db.query(Group).filter(Group.name.like('%Doctor%')).first()
if grp:
    print("Group table match:", grp.name, "-> JID:", grp.whatsapp_group_id)
else:
    print("No Group table match for Doctor, searching RawMessage/WhatsAppMessage for group JIDs...")
    # Find messages where raw text or group contains Doctor
    for m in msgs:
        if m.full_webhook_json:
            print("  Webhook JSON snippet:", str(m.full_webhook_json)[:200])
