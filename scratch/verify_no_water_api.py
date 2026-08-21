"""
Verify no water monitoring in API
"""
import urllib.request
import json

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=reminders"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    water_items = [r for r in data if 'water' in str(r).lower()]
    print(f"Total reminders in live API: {len(data)}")
    print(f"Water monitoring reminders in live API: {len(water_items)}")
    for item in data[:5]:
        if not item.get('__meta__'):
            print(f"ID: {item.get('id')} | Name: '{item.get('person_name')}' | Group: '{item.get('group_name')}' | Reports: '{item.get('report_types')}'")
