"""
Test live API endpoint with UTF-8 encoding output
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json
import time

timestamp = int(time.time())
url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=reminders&_t={timestamp}"

print(f"=== TESTING URL: {url} ===")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Cache-Control': 'no-cache, no-store', 'Pragma': 'no-cache'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8')
        print(f"HTTP Status: {resp.status}")
        data = json.loads(content)
        print(f"Total items returned: {len(data)}")
        water_count = 0
        for item in data:
            if item.get('__meta__'): continue
            pname = str(item.get('person_name', ''))
            notes = str(item.get('task_notes', ''))
            gid = str(item.get('whatsapp_group_id', ''))
            if 'water' in pname.lower() or 'water' in notes.lower() or 'water' in gid.lower():
                water_count += 1
                print(f"WATER ITEM: ID={item.get('id')} | Name='{pname}' | Notes='{notes}' | Group='{gid}'")
        print(f"Total Water Items in Response: {water_count}")
except Exception as e:
    print("Error:", e)
