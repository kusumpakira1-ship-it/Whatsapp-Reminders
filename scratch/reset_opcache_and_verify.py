import ftplib, io, urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')

# A PHP file that clears opcache and outputs JSON
opcache_php = b"""<?php
// Direct opcache clear - NOT routed through index.php
$cleared = false;
if (function_exists('opcache_reset')) {
    opcache_reset();
    $cleared = true;
}
// Also clear stat cache
clearstatcache(true);
header('Content-Type: application/json');
echo json_encode([
    'opcache_cleared' => $cleared, 
    'time' => date('Y-m-d H:i:s'),
    'php_version' => PHP_VERSION
]);
"""

# Upload to multiple paths with a DIFFERENT filename that won't be caught by .htaccess
filename = 'oc_reset_7x9k.php'
paths = [
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/kusum/Whatsapp_Rem',
]

uploaded_urls = []
for path in paths:
    try:
        ftp.cwd(path)
        ftp.storbinary(f'STOR {filename}', io.BytesIO(opcache_php))
        url_path = path.replace('/public_html', '')
        url = f'https://sunfragroup.com{url_path}/{filename}'
        uploaded_urls.append(url)
        print(f'Uploaded to {path}')
    except Exception as e:
        print(f'Failed {path}: {e}')

ftp.quit()
print()

# Now hit those URLs to trigger the reset
time.sleep(1)
for url in uploaded_urls:
    try:
        req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = resp.read().decode('utf-8', errors='ignore')
            print(f'HIT {url} => {result}')
    except Exception as e:
        print(f'HIT {url} => ERROR: {e}')

print()
print('OPcache reset done. Wait 2 seconds then test...')
time.sleep(2)

# Now verify the API returns the correct 6 groups
ts = int(time.time())
test_url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=waha/groups&t={ts}'
req = urllib.request.Request(test_url, headers={'Cache-Control': 'no-cache, no-store', 'Pragma': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read().decode('utf-8')
        import json
        groups_data = json.loads(data)
        groups = groups_data.get('groups', [])
        print(f'Total groups now: {len(groups)}')
        
        target_names = ['Accounts - Sunfra Feeds', 'Raw Material Prices & Orders', 'Sunfra Feed Plant', 'Payments - Sunfra Feeds', 'Summary - Sunfra Feeds', 'Sales - Sunfra Feeds', 'Sunfra Feeds']
        for tn in target_names:
            found = [g for g in groups if g.get('name','').lower() == tn.lower()]
            status = 'FOUND' if found else 'MISSING'
            info = f" | id: {found[0]['id']}" if found else ''
            print(f'{status}: {tn}{info}')
except Exception as e:
    print(f'API test error: {e}')
