import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from models import UnifiedReminder
from waha_service import get_session_status

db = get_db_session()
r = db.query(UnifiedReminder).filter(UnifiedReminder.id == 979).first()
if r:
    print(f"Before update: ID {r.id}, Frequency: '{r.frequency}', Status: {r.status}, Trigger: {r.trigger_time}")
    r.frequency = 'daily'
    db.commit()
    print(f"After update: ID {r.id}, Frequency: '{r.frequency}', Status: {r.status}, Trigger: {r.trigger_time}")
db.close()

# Also update in local sqlite files
import sqlite3
for sq_path in ['whatsapp_reminders.sqlite', 'backend/whatsapp_reminders.sqlite', 'backend/backend/whatsapp_reminders.sqlite', 'frontend/whatsapp_reminders.sqlite']:
    if os.path.exists(sq_path):
        s_conn = sqlite3.connect(sq_path)
        s_cur = s_conn.cursor()
        s_cur.execute("UPDATE sunfra_unified_reminders SET frequency = 'daily', status = 'pending', trigger_time = '2026-10-23 23:00:00' WHERE id = 979")
        s_conn.commit()
        s_conn.close()
        print(f"Updated sqlite file: {sq_path}")

# Check WAHA status
waha_status = get_session_status('default')
print(f"WAHA 'default' session status: {waha_status}")
