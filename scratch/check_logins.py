import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
import json
import requests
from datetime import datetime
from config import settings
from database import SessionLocal

sys.stdout.reconfigure(encoding='utf-8')

names = ['balaji', 'mahalakshmi', 'roopa', 'divya', '9493928388', '6364817749', '8686856459', '9381255565']

print("--- 1. Testing MySQL Connection ---")
try:
    db = SessionLocal()
    from sqlalchemy import text
    result = db.execute(text("SELECT id, sender, sender_name, group_name, raw_text, timestamp FROM raw_messages WHERE timestamp >= '2026-09-16 00:00:00' ORDER BY timestamp DESC LIMIT 50")).fetchall()
    print(f"Found {len(result)} raw messages today in MySQL:")
    for r in result:
        txt = (r[4] or "").lower()
        sndr = (r[1] or "").lower()
        if any(n in txt or n in sndr for n in names):
            print(f"MATCH -> Time: {r[5]} | Sender: {r[1]} ({r[2]}) | Group: {r[3]} | Text: {r[4]}")
        else:
            print(f"RAW  -> Time: {r[5]} | Sender: {r[1]} ({r[2]}) | Group: {r[3]} | Text: {r[4][:40]}")
    db.close()
except Exception as e:
    print(f"MySQL Error: {e}")

print("\n--- 2. Checking WAHA API for Target Groups ---")
waha_url = getattr(settings, 'WAHA_URL', 'http://localhost:3000').replace('host.docker.internal', 'localhost').rstrip('/')
headers = {'X-Api-Key': getattr(settings, 'WAHA_API_KEY', '123')}

groups = {
    'Jataayu (Roopa)': ['120363428881117777@g.us', '120363422729608263@g.us'],
    'Sunfra Corporate (Divya)': ['120363427470582988@g.us', '120363426659667927@g.us'],
    'Sunfra Farms (Mahalakshmi)': ['120363221285198390@g.us', '120363221211615047@g.us'],
    'Management Team (Balaji)': ['120363406924564250@g.us']
}

for group_name, jids in groups.items():
    print(f"\nGroup: {group_name}")
    for jid in jids:
        try:
            url = f"{waha_url}/api/default/chats/{jid}/messages?limit=15"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                msgs = res.json()
                print(f"  JID {jid}: fetched {len(msgs)} messages")
                for m in msgs:
                    if isinstance(m, dict):
                        body = m.get('body', '')
                        sender = m.get('from', '') or m.get('participant', '')
                        ts = m.get('timestamp')
                        if ts:
                            try:
                                dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                            except Exception:
                                dt = str(ts)
                        else:
                            dt = "N/A"
                        print(f"    [{dt}] {sender}: {body}")
            else:
                print(f"  JID {jid}: Failed HTTP {res.status_code}")
        except Exception as err:
            print(f"  JID {jid}: Error {err}")
