"""
Upload a PHP wrapper that executes the main index.php with CDN bypass headers.
This tricks the CDN into treating every request as dynamic/uncacheable.
"""
import ftplib, sys, io
sys.stdout.reconfigure(encoding='utf-8')

# This wrapper forces CDN bypass. Upload it as a test file first.
wrapper_php = b"""<?php
// Force CDN bypass - Hostinger hcdn respects these
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0, s-maxage=0');
header('Pragma: no-cache');
header('Vary: *');
header('Surrogate-Control: no-store');
// Also attempt opcache reset
if (function_exists('opcache_reset')) { opcache_reset(); }
clearstatcache(true);
echo 'CDN_BYPASS_TEST_OK_' . time();
"""

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR cdn_test.php', io.BytesIO(wrapper_php))
print("Uploaded cdn_test.php")
ftp.quit()

import urllib.request, time
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/cdn_test.php?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    result = resp.read().decode()
    headers = dict(resp.headers)
    print(f"Result: {result}")
    print(f"x-hcdn-cache-status: {headers.get('x-hcdn-cache-status', 'N/A')}")
    print(f"Cache-Control response: {headers.get('Cache-Control', 'N/A')}")
