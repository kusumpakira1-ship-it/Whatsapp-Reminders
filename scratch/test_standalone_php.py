"""
The marker_test.php is returning HTML content for index.php - meaning .htaccess is redirecting all requests to index.php.
This confirms the server IS serving our updated index.php but the browser/HTTP client is hitting a different (cached) version.

Let's check the ACTUAL index.php that GET requests hit by looking at the raw PHP output.
We need to disable the .htaccess redirect and upload a standalone marker PHP file.
"""

import ftplib, urllib.request, sys, io, time
sys.stdout.reconfigure(encoding='utf-8')

# Upload a completely standalone test file with NO connection to index.php
test_php = b"""<?php
// Standalone test - not connected to index.php
header('Cache-Control: no-store, no-cache');
header('Content-Type: text/plain');
echo 'STANDALONE_TEST_RESPONSE_OK_' . date('Y-m-d H:i:s');
echo '\\n';
echo 'PHP Version: ' . PHP_VERSION;
echo '\\n';
echo 'File: ' . __FILE__;
"""

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR standalone_test.php', io.BytesIO(test_php))
print("Uploaded standalone_test.php")
ftp.quit()

time.sleep(1)
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/standalone_test.php?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        headers = dict(resp.headers)
        print(f"URL: {url}")
        print(f"Response Content: {content}")
        print(f"x-hcdn-cache-status: {headers.get('x-hcdn-cache-status', 'N/A')}")
except Exception as e:
    print(f"Error: {e}")
