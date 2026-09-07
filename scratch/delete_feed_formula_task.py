import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. SQLite whatsapp_reminders.sqlite
conn_sqlite = sqlite3.connect('whatsapp_reminders.sqlite')
cursor_sqlite = conn_sqlite.cursor()

cursor_sqlite.execute("SELECT id, task_name, due_time, frequency, status FROM sunfra_tasks WHERE task_name LIKE '%feed formula%'")
rows = cursor_sqlite.fetchall()
print("Found in SQLite sunfra_tasks:", rows)

if rows:
    cursor_sqlite.execute("DELETE FROM sunfra_tasks WHERE task_name LIKE '%feed formula%'")
    conn_sqlite.commit()
    print("DELETED Feed Formula task(s) from SQLite whatsapp_reminders.sqlite!")

# 2. Check MySQL database if accessible
try:
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from database import SessionLocal
    from models import Task
    
    db = SessionLocal()
    mysql_tasks = db.query(Task).filter(Task.task_name.like('%feed formula%')).all()
    print("Found in MySQL tasks:", [(t.id, t.task_name) for t in mysql_tasks])
    
    if mysql_tasks:
        for t in mysql_tasks:
            db.delete(t)
        db.commit()
        print("DELETED Feed Formula task(s) from MySQL database!")
except Exception as e:
    print("MySQL check/delete error or not used:", e)
