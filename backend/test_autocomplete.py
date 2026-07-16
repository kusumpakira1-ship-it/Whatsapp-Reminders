import os
import sys
import logging
import urllib.parse
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Task, WhatsAppMessage, RawMessage
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

encoded_password = urllib.parse.quote_plus(settings.DB_PASS)
engine = create_engine(f"mysql+pymysql://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}/{settings.DB_NAME}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

now_ist = datetime.now()
print("Now IST:", now_ist)

pending_tasks = db.query(Task).filter(Task.status.in_(['pending', 'overdue'])).all()
print(f"Found {len(pending_tasks)} pending/overdue tasks.")

for t in pending_tasks:
    print(f"\nEvaluating Task ID: {t.id}, Name: {t.task_name}, Group: {t.whatsapp_group_id}, Phone: {t.assigned_person_phone}, Due: {t.due_time}")
    
    default_keywords = ['done', 'completed', 'finish', 'finished', 'ok done', 'complete', 'ho gaya', 'ho gya', 'kar diya', '✅', 'done✅']
    keywords = list(default_keywords)
    if t.completion_keywords:
        keywords.extend([x.strip().lower() for x in t.completion_keywords.split(',')])
    
    import re
    task_name_words = re.sub(r'[^a-zA-Z0-9\s]', '', t.task_name).lower().split()
    task_identifiers = [w for w in task_name_words if len(w) > 3 and w not in ['task', 'check', 'please', 'update', 'submit', 'report']]
    print(f"Task Identifiers: {task_identifiers}")
    
    since = t.due_time if t.due_time else (now_ist - timedelta(hours=24))
    all_messages = []
    
    if t.assigned_person_phone:
        phones_raw = [x.strip() for x in t.assigned_person_phone.split(',')]
        phone_patterns = []
        for ph in phones_raw:
            digits = "".join(filter(str.isdigit, ph))
            if len(digits) == 10: digits = "91" + digits
            if digits: phone_patterns.append(digits)
        print(f"Phone patterns: {phone_patterns}")
        if phone_patterns:
            from sqlalchemy import or_
            conditions = [RawMessage.sender.like(f"%{p}%") for p in phone_patterns]
            msgs = db.query(RawMessage.raw_text).filter(
                RawMessage.timestamp >= since,
                or_(*conditions)
            ).order_by(RawMessage.timestamp.desc()).limit(20).all()
            all_messages.extend([m[0] for m in msgs if m[0]])
            
    print(f"Found {len(all_messages)} recent messages.")
    for msg in all_messages:
        print(f" - Msg: {msg}")

