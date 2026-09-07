import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_reminders.sqlite')
c = conn.cursor()
c.execute("SELECT * FROM sunfra_tasks WHERE task_name LIKE '%feed formula%'")
print("SQLite Feed Formula tasks:", c.fetchall())

try:
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from database import SessionLocal
    from models import Task
    db = SessionLocal()
    m_tasks = db.query(Task).filter(Task.task_name.like('%feed formula%')).all()
    print("MySQL Feed Formula tasks:", [(t.id, t.task_name) for t in m_tasks])
except Exception as e:
    print("MySQL check error:", e)
