import ftplib, io

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')

# Upload a simple PHP file that is NOT affected by OPcache for waha/groups route test
test_php = b"""<?php
header('Content-Type: application/json');
require_once __DIR__ . '/index.php';
// This would have run index.php... but let's just test the count
echo json_encode(['test' => 'direct_php', 'status' => 'ok']);
?>"""

# Actually let's just hit the API directly and count chars
ftp.quit()

import urllib.request, json, time

ts = int(time.time())
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=waha/groups&nocache={ts}'
req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache'})
with urllib.request.urlopen(req, timeout=30) as resp:
    raw = resp.read()
    data = json.loads(raw.decode('utf-8'))
    groups = data.get('groups', [])
    print(f'Total groups returned by API: {len(groups)}')
    
    # Find the 7 missing groups by ID
    target_ids = [
        '120363429954274639',
        '120363429851145929', 
        '120363429180468592',
        '120363429948387845',
        '120363428748481277',
        '120363409756032304',
        '120363410508859526'
    ]
    print()
    for tid in target_ids:
        found = [g for g in groups if tid in str(g.get('id',''))]
        if found:
            print(f'FOUND: {found[0]}')
        else:
            print(f'NOT FOUND: {tid}')
    
    # Also check by name
    print()
    target_names = ['Accounts - Sunfra Feeds', 'Raw Material Prices & Orders', 'Sunfra Feed Plant', 'Payments - Sunfra Feeds', 'Summary - Sunfra Feeds', 'Sales - Sunfra Feeds', 'Sunfra Feeds']
    for tn in target_names:
        found = [g for g in groups if g.get('name','').lower() == tn.lower()]
        if found:
            print(f'NAME FOUND: {found[0]}')
        else:
            print(f'NAME NOT FOUND: {tn}')
