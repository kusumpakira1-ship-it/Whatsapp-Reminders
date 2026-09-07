import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage, WhatsAppMessage

db = SessionLocal()

search_numbers = ['19,05,317', '1905317', '7,17,140', '717140', '3,13,343', '313343', '9,61,959', '961959', '1,02,371', '102371']

print("Searching MySQL for physical numbers...")

raw_msgs = db.query(RawMessage).all()
for m in raw_msgs:
    txt = m.raw_text or ''
    for num in search_numbers:
        if num in txt:
            print(f"FOUND IN RawMessage ID {m.id} [{m.timestamp}] GRP: {m.group_name} | SND: {m.sender}")
            print("  TEXT:", txt)
            print("-" * 60)

wa_msgs = db.query(WhatsAppMessage).all()
for m in wa_msgs:
    txt = m.message_text or ''
    for num in search_numbers:
        if num in txt:
            print(f"FOUND IN WhatsAppMessage ID {m.id} [{m.timestamp}] GRP_ID: {m.group_id} | SND_ID: {m.sender_id}")
            print("  TEXT:", txt)
            print("-" * 60)

