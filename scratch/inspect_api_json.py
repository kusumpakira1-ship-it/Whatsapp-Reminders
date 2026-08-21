"""
Inspect exact JSON array returned from API.
"""
import urllib.request, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=reminders&date=2026-08-13&t={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})

with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode('utf-8', errors='ignore'))
    for r in data:
        print(f"ID: {r.get('id')} | Name: {r.get('person_name')} | Group: {r.get('group_name')} | SubStatus: {r.get('sub_reports_status')}")

