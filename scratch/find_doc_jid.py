import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('waha_groups.json', 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)
    for g in data:
        name = g.get('name') or g.get('subject') or ''
        gid = g.get('id') or g.get('jid') or ''
        if 'doc' in name.lower() or 'feedback' in name.lower() or 'manger' in name.lower() or 'manager' in name.lower():
            print(f"Name: '{name}' -> JID: {gid}")
