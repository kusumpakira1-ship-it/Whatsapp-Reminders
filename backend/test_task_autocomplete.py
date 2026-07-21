import os
import sys
import re
from datetime import datetime, timezone, timedelta

sys.path.append('/app')
from database import SessionLocal
from models import Task, RawMessage

db = SessionLocal()
IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

pending_tasks = db.query(Task).filter(Task.status.in_(['pending', 'overdue'])).all()

raw_msgs_recent = db.query(RawMessage).filter(
    RawMessage.timestamp >= now_ist - timedelta(days=7)
).order_by(RawMessage.timestamp.asc()).all()

def check_task_match(task, msg_text):
    tn = task.task_name.lower()
    msg = msg_text.lower()
    
    # Needs meeting indicator
    has_meeting_context = any(w in msg for w in ['meeting', 'conducted', 'conduct', 'done', 'completed', 'finished', 'checklist'])
    if not has_meeting_context:
        return False

    if 'egg godown' in tn and any(w in msg for w in ['egg godown', 'godown']):
        return True
    if 'feed plant' in tn and any(w in msg for w in ['feed plant', 'plant']):
        return True
    if 'supervisor' in tn and any(w in msg for w in ['supervisor', 'supervisors']):
        return True
    if ('medicine' in tn or 'incharge' in tn) and any(w in msg for w in ['medicine', 'incharge', 'incharges', 'water']):
        return True
    if 'shed worker' in tn and ('shed worker' in msg or 'shed workers' in msg or ('shed' in msg and 'worker' in msg)):
        if not any(x in msg for x in ['godown', 'plant', 'supervisor', 'medicine', 'incharge']):
            return True
            
    return False

print(f"=== TESTING PERFECT TASK MATCHING FOR ALL 5 MEETING TASKS ===")
for t in pending_tasks:
    matched_msg = None
    for m in raw_msgs_recent:
        if check_task_match(t, str(m.raw_text or '')):
            matched_msg = m
            break

    if matched_msg:
        print(f"✅ ID {t.id:2d} ('{t.task_name}') -> [{matched_msg.timestamp}] {matched_msg.group_name} | {matched_msg.sender}: {matched_msg.raw_text[:70]}")
    else:
        print(f"❌ ID {t.id:2d} ('{t.task_name}') -> No Match")
