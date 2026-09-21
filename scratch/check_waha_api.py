import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

waha_url = "http://localhost:3000"
session = "default"

try:
    r = requests.get(f"{waha_url}/api/{session}/chats", timeout=10)
    if r.status_code == 200:
        chats = r.json()
        print(f"Total chats in WAHA: {len(chats)}")
        for c in chats[:15]:
            print("Chat:", c.get("id"), "| Name:", c.get("name"))
    else:
        print("WAHA Status:", r.status_code, r.text)
except Exception as e:
    print("Error querying WAHA:", e)
