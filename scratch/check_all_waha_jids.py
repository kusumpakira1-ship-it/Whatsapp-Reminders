import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

waha_url = "http://localhost:3000"
session = "default"
headers = {"X-Api-Key": "123"}

group_jids = {
    "AI & IOT": "120363429469512014@g.us",
    "Sunfra OLX CEE": "120363428895707621@g.us",
    "Jataayu": "120363428881117777@g.us",
    "Sunfra Corporate": "120363427470582988@g.us",
    "Sunfra Mudah": "120363410545216320@g.us",
    "Sunfra HR Team": "120363431222906850@g.us",
    "Indus": "120363409533299483@g.us",
    "Sunfra Farms": "120363221285198390@g.us",
    "Sunfra Feeds": "120363412616266332@g.us",
    "Management Team": "120363406924564250@g.us",
    "Tendered": "120363411380848761@g.us"
}

print("================ DIRECT WAHA MESSAGE FETCH FOR ALL 11 GROUPS FOR TODAY ================")

for g_name, jid in group_jids.items():
    print(f"\n================ GROUP: {g_name} ({jid}) ================")
    try:
        r = requests.get(f"{waha_url}/api/{session}/chats/{jid}/messages?limit=50", headers=headers, timeout=10)
        if r.status_code == 200:
            msgs = r.json()
            print(f"Total messages in chat: {len(msgs)}")
            for m in msgs:
                sender = m.get("from") or m.get("author")
                push_name = m.get("_data", {}).get("notifyName") or m.get("pushName") or ""
                body = (m.get("body") or "").replace('\n', ' | ')
                ts = m.get("timestamp")
                print(f"  [{ts}] Sender: {sender} ({push_name}) | Text: '{body}'")
        else:
            print("Status:", r.status_code, r.text)
    except Exception as e:
        print(f"Error fetching {g_name}: {e}")
