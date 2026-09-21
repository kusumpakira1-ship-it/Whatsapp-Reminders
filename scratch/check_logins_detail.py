import os
import sys
from dotenv import load_dotenv

# Load root .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_dir)

from database import get_db_session
from models import RawMessage, WhatsAppMessage
import requests

sys.stdout.reconfigure(encoding='utf-8')

print("==================================================")
print("🔍 CHECKING LOGINS FOR: Balaji, Mahalakshmi, Roopa, Divya")
print("==================================================")

db = get_db_session()

names = ['balaji', 'mahalakshmi', 'roopa', 'divya']
phones = ['9493928388', '6364817749', '8686856459', '9381255565']

print("\n--- 1. Querying raw_messages in Database (Today: 2026-09-16) ---")
try:
    raws = db.query(RawMessage).filter(RawMessage.timestamp >= '2026-09-16 00:00:00').order_by(RawMessage.timestamp.desc()).all()
    print(f"Total RawMessage entries today: {len(raws)}")
    found = 0
    for r in raws:
        txt = (r.raw_text or "").lower()
        sender_str = (r.sender or "").lower()
        sender_name = (r.sender_name or "").lower()
        phone_str = (r.sender_phone or "").lower()
        
        if any(n in txt or n in sender_str or n in sender_name or n in phone_str for n in names + phones):
            found += 1
            print(f"✅ FOUND MATCH -> [{r.timestamp}] Sender: {r.sender} | Name: {r.sender_name} | Phone: {r.sender_phone} | Group: {r.group_name}\n   Text: {r.raw_text}\n")
    if found == 0:
        print("❌ No matching raw messages found in DB for today for these 4 individuals.")
except Exception as e:
    print(f"DB Query Error: {e}")

print("\n--- 2. Checking Recent RawMessages for past 3 days (14-16 Sep) ---")
try:
    raws_recent = db.query(RawMessage).filter(RawMessage.timestamp >= '2026-09-14 00:00:00').order_by(RawMessage.timestamp.desc()).all()
    print(f"Total RawMessages in last 3 days: {len(raws_recent)}")
    for r in raws_recent:
        txt = (r.raw_text or "").lower()
        sender_str = (r.sender or "").lower()
        sender_name = (r.sender_name or "").lower()
        phone_str = (r.sender_phone or "").lower()
        
        if any(n in txt or n in sender_str or n in sender_name or n in phone_str for n in names + phones):
            print(f"  [{r.timestamp}] Sender: {r.sender_name} ({r.sender_phone}) | Group: {r.group_name} | Text: {r.raw_text}")
except Exception as e:
    print(f"Recent Query Error: {e}")

db.close()
