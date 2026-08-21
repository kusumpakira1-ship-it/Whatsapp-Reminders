"""
Purge LiteSpeed Server Cache on Hostinger
"""

import ftplib, urllib.request, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

purge_php = b"""<?php
header('X-LiteSpeed-Purge: *');
header('Cache-Control: no-cache, no-store, must-revalidate, max-age=0');
if (function_exists('opcache_reset')) { opcache_reset(); }
clearstatcache(true);
echo 'LITESPEED_CACHE_PURGED_SUCCESSFULLY';
"""

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

dirs = [
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html'
]

for d in dirs:
    try:
        ftp.cwd(d)
        ftp.storbinary('STOR purge_cache.php', io.BytesIO(purge_php))
        print(f"Stored purge_cache.php in {d}")
    except Exception as e:
        print(f"Error {d}: {e}")

ftp.quit()

time.sleep(1)
urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/purge_cache.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/purge_cache.php',
    'https://sunfragroup.com/purge_cache.php'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        res = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        print(f"Trigger {u} => {res}")
    except Exception as e:
        print(f"Trigger {u} error: {e}")

time.sleep(2)
# Re-test unique tag
unique_tag = "BUILD_TAG_1786606172"
test_url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?cache_bust={int(time.time())}"
req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    found_tag = unique_tag in html
    print(f"\nAfter Purging LiteSpeed Cache on {test_url}:")
    print(f"• Tag {unique_tag} found? {'YES ✅' if found_tag else 'NO ❌'}")
