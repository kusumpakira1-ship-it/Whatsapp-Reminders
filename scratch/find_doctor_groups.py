import json
import sqlite3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import SessionLocal
from models import RawMessage, WhatsAppMessage, Group

db = SessionLocal()

print("=== SEARCHING RAW MESSAGES FOR 'Doctor' OR 'Feedback' ===")
raws = db.query(RawMessage).filter(RawMessage.group_name.like('%doc%') | RawMessage.group_name.like('%feedback%') | RawMessage.group_name.like('%manager%')).all()
for r in raws[:20]:
    print("RAW GRP:", r.group_name, "| Sender:", r.sender)

was = db.query(WhatsAppMessage).filter(WhatsAppMessage.group_id.like('%doc%') | WhatsAppMessage.group_id.like('%feedback%') | WhatsAppMessage.group_id.like('%manager%')).all()
for w in was[:20]:
    print("WA GRP_ID:", w.group_id, "| Sender:", w.sender_id)

print("\n=== SEARCHING ALL RAW MESSAGE GROUP NAMES EVER LOGGED ===")
c = db.execute(sqlite3.text("SELECT DISTINCT group_name FROM sunfra_raw_messages WHERE group_name IS NOT NULL") if hasattr(db, 'execute') else "SELECT 1").fetchall() if False else None
from sqlalchemy import text
res = db.execute(text("SELECT DISTINCT group_name FROM sunfra_raw_messages WHERE group_name IS NOT NULL")).fetchall()
print("Distinct Group Names in RawMessage:")
for r in res:
    print(" -", r[0])
