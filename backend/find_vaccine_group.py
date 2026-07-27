import sys, os
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from dotenv import load_dotenv
load_dotenv(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\.env')

from database import SessionLocal
from models import RawMessage, Group
from sqlalchemy import func

db = SessionLocal()

print("=== All Groups in DB ===")
all_groups = db.query(Group).all()
for g in all_groups:
    print(f"  name={g.name} | whatsapp_group_id={g.whatsapp_group_id}")

print()
print("=== Groups with 'vaccine' in name ===")
vgroups = db.query(Group).filter(func.lower(Group.name).contains('vaccine')).all()
for g in vgroups:
    print(f"  name={g.name} | whatsapp_group_id={g.whatsapp_group_id}")
if not vgroups:
    print("  None found with 'vaccine'")

print()
print("=== Raw messages mentioning vaccine ===")
try:
    msgs = db.query(RawMessage).filter(
        func.lower(RawMessage.sender).contains('vaccine')
    ).limit(10).all()
    for m in msgs:
        print(f"  sender={m.sender}")
    if not msgs:
        print("  None found in sender field")
except Exception as e:
    print(f"Error querying raw messages: {e}")

print()
print("=== WhatsApp groups from WAHA ===")
try:
    import requests
    WAHA_URL = os.getenv("WAHA_URL", "http://localhost:3000")
    WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
    WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
    headers = {"X-Api-Key": WAHA_API_KEY} if WAHA_API_KEY else {}
    r = requests.get(f"{WAHA_URL}/api/{WAHA_SESSION}/chats?limit=100", headers=headers, timeout=10)
    if r.status_code == 200:
        chats = r.json()
        for chat in chats:
            name = chat.get("name", "") or ""
            cid = chat.get("id", "")
            if "vaccine" in name.lower() or "vacc" in name.lower():
                print(f"  FOUND: name={name} | id={cid}")
        # Also show all group chats
        print()
        print("  All group chats:")
        for chat in chats:
            if "@g.us" in chat.get("id", ""):
                print(f"    name={chat.get('name')} | id={chat.get('id')}")
    else:
        print(f"  WAHA returned status {r.status_code}")
except Exception as e:
    print(f"  WAHA error: {e}")

db.close()
