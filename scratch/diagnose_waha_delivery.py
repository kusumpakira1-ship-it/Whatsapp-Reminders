import sys, os, requests, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from waha_service import send_waha_message, get_session_status

print("=== 1. Checking WAHA Session Status ===")
waha_url = os.getenv("WAHA_URL", "http://localhost:3000")
print(f"WAHA URL: {waha_url}")

try:
    sess_res = requests.get(f"{waha_url}/api/sessions", timeout=5)
    print("WAHA Sessions Status Code:", sess_res.status_code)
    print("WAHA Sessions Output:", json.dumps(sess_res.json(), indent=2))
except Exception as e:
    print("WAHA Connection Error:", e)

print("\n=== 2. Sending Direct Test WhatsApp Message ===")
target_jid = "917259510983@c.us"
payload = {
    "chatId": target_jid,
    "text": "🔔 *Diagnostic Test Message*\n\nHello Kusum! Testing WhatsApp WAHA delivery connection right now.",
    "session": "default"
}

try:
    msg_res = requests.post(f"{waha_url}/api/sendText", json=payload, timeout=10)
    print("WAHA SendText HTTP Status:", msg_res.status_code)
    print("WAHA SendText Response:", msg_res.text)
except Exception as e:
    print("WAHA SendText Exception:", e)
