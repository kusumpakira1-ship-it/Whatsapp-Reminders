import requests
import json
import sys
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

IST = timezone(timedelta(hours=5, minutes=30))
WAHA_URL = "http://localhost:3000"
HEADERS = {"X-Api-Key": "123"}

print("--- FETCHING GROUPS FROM WAHA ---")
res = requests.get(f"{WAHA_URL}/api/default/groups", headers=HEADERS)
if res.status_code != 200:
    print(f"Failed groups: {res.status_code} {res.text}")
    res = requests.get(f"{WAHA_URL}/api/default/chats", headers=HEADERS)

if res.status_code == 200:
    groups = res.json()
    print(f"Total groups found: {len(groups)}")
    
    target_jids = {}
    for g in groups:
        name = g.get("name", "")
        raw_id = g.get("id", "")
        gid = raw_id.get("_serialized", str(raw_id)) if isinstance(raw_id, dict) else str(raw_id)
        
        # Look for Sunfra Mudah & AI & IOT
        if name in ["AI & IOT", "Sunfra Mudah", "Sunfra HR Team", "Sunfra Corporate", "Sunfra OLX CEE"]:
            print(f"Target Group: '{name}' | ID: {gid}")
            target_jids[name] = gid

    print("\n--- FETCHING MESSAGES FROM TARGET GROUPS FOR 09 SEP 2026 ---")

    for gname, gid in target_jids.items():
        print(f"\n==========================================")
        print(f"Fetching messages for Group: {gname} ({gid})")
        print(f"==========================================")
        msg_res = requests.get(f"{WAHA_URL}/api/default/chats/{gid}/messages?limit=100", headers=HEADERS)
        if msg_res.status_code == 200:
            msgs = msg_res.json()
            print(f"Total messages in chat history: {len(msgs)}")
            for m in msgs:
                ts = m.get("timestamp", 0)
                dt_str = datetime.fromtimestamp(ts, tz=IST).strftime("%Y-%m-%d %H:%M:%S")
                # Filter for Sept 9 or Sept 10
                if "2026-09-09" in dt_str or "2026-09-10" in dt_str:
                    sender = m.get("from", m.get("_data", {}).get("author", ""))
                    if isinstance(sender, dict):
                        sender = sender.get("_serialized", str(sender))
                    author = m.get("_data", {}).get("author", "")
                    if isinstance(author, dict):
                        author = author.get("_serialized", str(author))
                    pushname = m.get("_data", {}).get("notifyName", m.get("pushName", ""))
                    body = m.get("body", m.get("text", ""))
                    from_me = m.get("fromMe", False)
                    print(f"[{dt_str}] Sender: {sender} | Author: {author} ({pushname}) | fromMe: {from_me} | Body: {repr(body)}")
        else:
            print(f"Failed to fetch messages for {gname}: {msg_res.status_code} {msg_res.text}")
