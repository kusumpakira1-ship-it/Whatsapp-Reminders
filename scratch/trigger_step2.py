import sys
sys.path.append('/app')

from database import SessionLocal
from models import Task
from scheduler import send_waha_message

db = SessionLocal()
task = db.query(Task).filter(Task.id == 82).first()
if task:
    task.status = 'pending_update'
    task.completion_details = 'Approved by Kusuma (7259510983)'
    db.commit()

group_reminder_msg = """⏰ *Reminder*

Hi Team,
*Task:* Feed Formula - Shead 5 to PLM (Week 16) need to be updated.

Please complete this work and reply to this message with "updated" or "completed" once finished."""

send_waha_message('120363410607412989@g.us', group_reminder_msg)
print("Successfully triggered Step 2 group reminder to Feed Formula group!")

db.close()
