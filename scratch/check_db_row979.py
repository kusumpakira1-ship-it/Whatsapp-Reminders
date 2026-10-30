import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session, _is_mysql_in_cooldown
from models import UnifiedReminder

print("Is MySQL in cooldown:", _is_mysql_in_cooldown())
db = get_db_session()
print("Session bind engine:", db.bind.name)

r = db.query(UnifiedReminder).filter(UnifiedReminder.id == 979).first()
if r:
    print(f"ID: {r.id}")
    print(f"Person: {r.person_name}")
    print(f"Group: {r.whatsapp_group_id}")
    print(f"Trigger Time: {r.trigger_time}")
    print(f"Status: {r.status}")
    print(f"Frequency: '{r.frequency}'")
    print(f"Repeat Interval: {r.repeat_interval}")
    print(f"Task Notes: {r.task_notes}")
else:
    print("Row 979 not found!")

db.close()
