import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage

db = SessionLocal()
m = db.query(RawMessage).filter(RawMessage.group_name == 'Doctor and Manager Daily Feedback').first()
if m:
    print("Found RawMessage for Doctor and Manager Daily Feedback:")
    print("  id:", m.id, "| sender:", m.sender, "| group_name:", m.group_name)
    if m.full_webhook_json:
        if isinstance(m.full_webhook_json, dict):
            payload = m.full_webhook_json.get('payload', {})
            print("  chatId:", payload.get('from') or payload.get('chatId'))
        else:
            print("  json:", str(m.full_webhook_json)[:300])
else:
    print("Not found")
