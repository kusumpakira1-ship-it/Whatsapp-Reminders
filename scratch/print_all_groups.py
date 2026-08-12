import urllib.request, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

ts = int(time.time())
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=waha/groups&t={ts}'
req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache, no-store', 'Pragma': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    raw = resp.read().decode('utf-8', errors='ignore')
    
# The full response - check length
print(f'Raw response length: {len(raw)} chars')

# Parse
data = json.loads(raw)
groups = data.get('groups', [])
print(f'Total groups: {len(groups)}')
print()

# Print ALL groups sorted by name (show first 30 chars of ID)
print('All groups:')
for g in groups:
    name = g.get('name', 'NONAME')
    gid = g.get('id', 'NOID')
    print(f'  {name[:50]:<50} | {gid}')
