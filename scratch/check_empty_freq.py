import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from models import UnifiedReminder

db = get_db_session()
rows = db.query(UnifiedReminder).all()
print(f"Total unified reminders: {len(rows)}")
for r in rows:
    if not r.frequency or r.frequency.strip() == '':
        print(f"ID {r.id} ({r.person_name}): empty frequency! Status: {r.status}, Trigger: {r.trigger_time}")
db.close()
