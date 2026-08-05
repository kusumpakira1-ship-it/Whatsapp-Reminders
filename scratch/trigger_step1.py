import sys
sys.path.append('/app')

from database import SessionLocal
from models import Task
from scheduler import send_waha_message

db = SessionLocal()
task = db.query(Task).filter(Task.id == 82).first()
if task:
    task.status = 'pending_approval'
    task.completion_details = None
    db.commit()
    print(f"Task {task.id} status reset to 'pending_approval'.")

msg = """🔔 *Feed Formula Approval Needed*

*Task:* Feed Formula - Shead 5 to PLM (Week 16)
*Status:* Pending Approval 🟡

Please reply with "send" to approve and confirm."""

approvers = ["917259510983@c.us", "916364817749@c.us"]
for app in approvers:
    send_waha_message(app, msg)
    print(f"Sent Step 1 private approval request to {app}")

db.close()
