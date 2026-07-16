import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Task

encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
engine = create_engine(f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}")
db = sessionmaker(bind=engine)()

tasks = db.query(Task).order_by(Task.id.desc()).all()
for t in tasks:
    print(f"[{t.id}] '{t.task_name}' - {t.status} - Due: {t.due_time} - Assignee: {t.assigned_person_phone}")
