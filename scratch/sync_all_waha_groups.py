"""
Sync all live groups from WAHA into sunfra_groups database table
and update waha_groups.json so all group JIDs display their human names on the website.
"""

import sys, os, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from models import Group

# 1. Fetch live groups from WAHA
req = urllib.request.Request('http://localhost:3000/api/default/groups', headers={'X-Api-Key': '123'})
waha_raw = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))

waha_list = []
for g in waha_raw:
    if isinstance(g, dict):
        gid = g.get('id')
        if isinstance(gid, dict):
            gid = gid.get('_serialized')
        name = g.get('name') or g.get('subject') or g.get('name')
        if gid and name:
            waha_list.append({'id': str(gid), 'name': str(name)})

print(f"Fetched {len(waha_list)} groups from WAHA.")

# 2. Update DB table sunfra_groups
db = SessionLocal()
added_count = 0
updated_count = 0

for item in waha_list:
    jid = item['id']
    name = item['name']
    
    existing = db.query(Group).filter(Group.whatsapp_group_id == jid).first()
    if not existing:
        new_g = Group(name=name, whatsapp_group_id=jid)
        db.add(new_g)
        added_count += 1
    else:
        if existing.name != name:
            existing.name = name
            updated_count += 1

db.commit()
db.close()
print(f"DB Sync Complete: Added {added_count} new groups, Updated {updated_count} group names.")

# 3. Update waha_groups.json in root
waha_json_path = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\waha_groups.json"
with open(waha_json_path, 'w', encoding='utf-8') as f:
    json.dump(waha_list, f, indent=2, ensure_ascii=False)

print(f"Updated waha_groups.json with {len(waha_list)} groups!")
