"""
Inspect matched items with UTF-8 reconfigure
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=reminders"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    water_count = 0
    for item in data:
        if item.get('__meta__'): continue
        pname = str(item.get('person_name', ''))
        notes = str(item.get('task_notes', ''))
        gid = str(item.get('whatsapp_group_id', ''))
        if 'water' in pname.lower() or 'water' in notes.lower() or 'water' in gid.lower():
            water_count += 1
            print(f"MATCH: ID={item.get('id')} | Name='{pname}' | Notes='{notes}' | Group='{gid}'")
    print(f"\nTOTAL WATER MATCHES FOUND: {water_count}")
