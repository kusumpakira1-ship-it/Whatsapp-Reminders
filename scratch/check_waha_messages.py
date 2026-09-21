import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

waha_url = "http://localhost:3000"
session = "default"
headers = {"X-Api-Key": "123"}

try:
    r = requests.get(f"{waha_url}/api/{session}/chats", headers=headers, timeout=10)
    if r.status_code == 200:
        chats = r.json()
        print(f"Total chats in WAHA: {len(chats)}")
        
        # Target groups for our 10 companies
        target_group_names = [
            "ai & iot", "sunfra olx cee", "jataayu", "sunfra corporate",
            "sunfra mudah", "sunfra hr team", "indus", "sunfra farms",
            "sunfra feeds", "management team", "tendered"
        ]
        
        for c in chats:
            c_name = str(c.get("name") or "").lower()
            c_id = c.get("id")
            
            if any(tg in c_name for tg in target_group_names) or "120363" in str(c_id):
                print(f"\n================ CHAT: [{c.get('name')}] ({c_id}) ================")
                # Fetch last 30 messages in this chat
                res_m = requests.get(f"{waha_url}/api/{session}/chats/{c_id}/messages?limit=30", headers=headers, timeout=10)
                if res_m.status_code == 200:
                    msgs = res_m.json()
                    for m in msgs:
                        # Print timestamp, sender, text
                        ts = m.get("timestamp")
                        from_user = m.get("from") or m.get("author")
                        body = (m.get("body") or "").replace('\n', ' | ')
                        push_name = m.get("_data", {}).get("notifyName") or m.get("pushName") or ""
                        print(f"  [{ts}] Sender: {from_user} ({push_name}) | Text: '{body}'")
    else:
        print("WAHA Status:", r.status_code, r.text)
except Exception as e:
    print("Error querying WAHA:", e)
