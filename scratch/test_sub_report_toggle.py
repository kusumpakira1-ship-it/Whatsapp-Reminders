"""
Test sub-report toggle API with action in payload
"""
import urllib.request
import json

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=sub_report_status"

payload = json.dumps({
    "action": "sub_report_status",
    "reminder_id": 185,
    "report_name": "Day book",
    "status": "pending"
}).encode('utf-8')

print("=== 1. TOGGLING 'Day book' TO 'pending' FOR REMINDER 185 ===")
try:
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("API Response:", res)
except Exception as e:
    print("API Error:", e)

payload_done = json.dumps({
    "action": "sub_report_status",
    "reminder_id": 185,
    "report_name": "Day book",
    "status": "done"
}).encode('utf-8')

print("\n=== 2. TOGGLING 'Day book' BACK TO 'done' FOR REMINDER 185 ===")
try:
    req = urllib.request.Request(url, data=payload_done, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, method='POST')
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("API Response:", res)
except Exception as e:
    print("API Error:", e)
