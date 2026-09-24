from database import SessionLocal
from models import Task

db = SessionLocal()
try:
    tasks = db.query(Task).filter(Task.status != 'completed').all()
    count = 0
    for t in tasks:
        if t.completion_details:
            t.completion_details = None
            count += 1
    db.commit()
    print(f"Cleared old completion details for {count} tasks via SQLAlchemy!")
except Exception as e:
    print("Error:", e)
finally:
    db.close()
