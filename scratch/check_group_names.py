import sys, os, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import SessionLocal
from models import Group

target_jids = ['120363429851145929@g.us', '120363429954274639@g.us']

db = SessionLocal()

print('=== DB SUNFRA_GROUPS CHECK ===')
for jid in target_jids:
    g = db.query(Group).filter(Group.whatsapp_group_id == jid).first()
    if g:
        print(f'JID: {jid} | DB Name: {g.name}')
    else:
        print(f'JID: {jid} | DB Name: NOT IN DB')

print('\n=== ALL DB GROUPS ===')
all_g = db.query(Group).all()
for g in all_g:
    print(f'  {g.name:35s} | {g.whatsapp_group_id}')

print('\n=== WAHA GROUPS CHECK ===')
try:
    req = urllib.request.Request('http://localhost:3000/api/default/groups', headers={'X-Api-Key': '123'})
    waha_groups = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    waha_map = {}
    for g in waha_groups:
        if isinstance(g, dict):
            gid = g.get('id')
            if isinstance(gid, dict):
                gid = gid.get('_serialized')
            if gid:
                waha_map[str(gid)] = g.get('name') or g.get('subject') or g.get('name')
                
    for jid in target_jids:
        print(f"JID: {jid} | WAHA Name: {waha_map.get(jid, 'NOT FOUND IN WAHA')}")
    
    print("\n--- WAHA GROUPS MATCHING TARGETS ---")
    for gid, gname in waha_map.items():
        if any(t in gid for t in ['120363429851145929', '120363429954274639']):
            print(f"  MATCH: {gid} -> {gname}")
            
except Exception as e:
    print('WAHA Groups API Error:', e)

db.close()
