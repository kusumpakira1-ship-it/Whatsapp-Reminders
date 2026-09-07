import sys, os
from datetime import datetime

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

from database import get_db_session, SqliteSession
from models import Task, Group
from waha_service import send_waha_message

group_name = 'Doctor and Manager Daily Feedback'
group_jid = '120363409816800438@g.us'

def setup_tasks_in_db(sess_fn, db_label):
    try:
        db = sess_fn()
        # 1. Ensure Group in sunfra_groups
        existing_group = db.query(Group).filter(Group.whatsapp_group_id == group_jid).first()
        if not existing_group:
            new_grp = Group(name=group_name, whatsapp_group_id=group_jid)
            db.add(new_grp)
            db.commit()
            print(f"[{db_label}] Created group entry: {group_name} ({group_jid})")
        else:
            print(f"[{db_label}] Group entry already exists.")

        # 2. Insert or update Tank A Cleaning task
        task_a = db.query(Task).filter(Task.task_name == 'Tank A Cleaning Reminder', Task.whatsapp_group_id == group_jid).first()
        if not task_a:
            task_a = Task(
                task_name='Tank A Cleaning Reminder',
                task_type='cleaning',
                assigned_person_name='Team',
                assigned_person_phone='1234567890',
                whatsapp_group_id=group_jid,
                due_time=datetime(2026, 9, 5, 11, 0, 0),
                completion_keywords='cleaned,done,completed',
                status='pending',
                frequency='monthly',
                repeat_interval='1h'
            )
            db.add(task_a)
            print(f"[{db_label}] Created Task A")
        else:
            task_a.due_time = datetime(2026, 9, 5, 11, 0, 0)
            task_a.status = 'pending'
            task_a.frequency = 'monthly'
            task_a.repeat_interval = '1h'
            task_a.completion_keywords = 'cleaned,done,completed'
            print(f"[{db_label}] Updated Task A")

        # 3. Insert or update Tank B Cleaning task
        task_b = db.query(Task).filter(Task.task_name == 'Tank B Cleaning Reminder', Task.whatsapp_group_id == group_jid).first()
        if not task_b:
            task_b = Task(
                task_name='Tank B Cleaning Reminder',
                task_type='cleaning',
                assigned_person_name='Team',
                assigned_person_phone='1234567890',
                whatsapp_group_id=group_jid,
                due_time=datetime(2026, 9, 11, 11, 0, 0),
                completion_keywords='cleaned,done,completed',
                status='pending',
                frequency='monthly',
                repeat_interval='1h'
            )
            db.add(task_b)
            print(f"[{db_label}] Created Task B")
        else:
            task_b.due_time = datetime(2026, 9, 11, 11, 0, 0)
            task_b.status = 'pending'
            task_b.frequency = 'monthly'
            task_b.repeat_interval = '1h'
            task_b.completion_keywords = 'cleaned,done,completed'
            print(f"[{db_label}] Updated Task B")

        db.commit()
        db.close()
    except Exception as e:
        print(f"[{db_label}] Error: {e}")

if __name__ == '__main__':
    setup_tasks_in_db(get_db_session, 'Primary DB')
    setup_tasks_in_db(SqliteSession, 'SQLite DB')

    # Send immediate alert for Tank A to group as requested by user
    msg = (
        "⏰ *TANK A CLEANING REMINDER* 🧼\n\n"
        "Hi Team,\n"
        "The task *\"Tank A Cleaning Reminder\"* was due on 5th Sep and is currently NOT cleaned.\n\n"
        "Please clean Tank A and reply to this group with *\"cleaned\"* or *\"done\"* once finished.\n\n"
        "Thank you! 🌱"
    )
    print("Sending immediate WA message for Tank A...")
    sent = send_waha_message(group_jid, msg)
    print(f"Immediate message dispatch result: {sent}")
