import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from datetime import datetime, timezone, timedelta
from database import SessionLocal
from models import RawMessage, ProcessedData, UnifiedReminder, Group
from sqlalchemy import func

IST = timezone(timedelta(hours=5, minutes=30))
today = datetime.now(IST).date()

db = SessionLocal()

print(f"=== CHECKING GATE MANAGER & MEETING SUBMISSIONS FOR TODAY ({today}) ===\n")

# 1. Fetch Gate Manager Group JID
gate_group = db.query(Group).filter(Group.name.ilike('%gate manager%')).first()
gate_jid = gate_group.whatsapp_group_id if gate_group else '120363225998735559@g.us'
print(f"Gate Manager Group JID: {gate_jid} | Name: {gate_group.name if gate_group else 'Gate Manager'}")

# 2. Fetch all raw messages today
raw_msgs = db.query(RawMessage).filter(func.date(RawMessage.timestamp) == today).all()
print(f"Total raw messages in DB today: {len(raw_msgs)}")

gate_msgs = []
for m in raw_msgs:
    txt = (m.raw_text or '').lower()
    g_name = (m.group_name or '').lower()
    if 'gate' in g_name or 'meeting' in txt or 'worker' in txt or 'follow' in txt or 'shed' in txt:
        gate_msgs.append(m)

print(f"\nFound {len(gate_msgs)} relevant messages today:")
for m in gate_msgs:
    print(f"  [{m.timestamp}] Sender: {m.sender} | Group: {m.group_name} | Text: {m.raw_text}")

# 3. Fetch all processed data today
proc_msgs = db.query(ProcessedData).filter(func.date(ProcessedData.processed_time) == today).all()
print(f"\nTotal ProcessedData rows today: {len(proc_msgs)}")
for p in proc_msgs:
    txt = (p.notes or '').lower()
    if 'meeting' in txt or 'gate' in txt or 'worker' in txt:
        print(f"  ProcessedData: {p.sender} | Group: {p.group_name} | Notes: {p.notes} | Cat: {p.category}")

# 4. Fetch reminders matching Meeting / Gate Manager
reminders = db.query(UnifiedReminder).filter(UnifiedReminder.report_types.ilike('%meeting%')).all()
print(f"\nFound {len(reminders)} Meeting reminders in DB:")
for r in reminders:
    print(f"  ID: {r.id} | Group: {r.whatsapp_group_id} | Reports: {r.report_types} | Time: {r.trigger_time} | Status: {r.status}")

db.close()
