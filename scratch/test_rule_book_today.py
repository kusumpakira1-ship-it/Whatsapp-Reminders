"""
Test matching Mahalakshmi's Rule Book message today (14 Aug 2026) in scheduler.py.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
import json
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage

db = SessionLocal()

start_of_day = datetime.datetime(2026, 8, 14, 0, 0, 0)
msgs = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day).all()

for m in msgs:
    txt = (m.raw_text or '').lower()
    grp = (m.group_name or '').lower()
    if 'rule' in txt or '120363430772426306' in grp:
        print(f"Found Rule message today! Sender: {m.sender} | Group: {grp} | Text: {txt}")

db.close()

