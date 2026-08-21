"""
The root issue:
- /public_html/.htaccess has: RewriteRule ^(.*)$ index.php [L]
  This means ALL requests to sunfragroup.com/* go to /public_html/index.php (232734 bytes old)

BUT actually, looking more carefully at the htaccess rules:
- RewriteCond %{REQUEST_FILENAME} !-f  (only redirects if file doesn't exist)
- RewriteCond %{REQUEST_FILENAME} !-d  (only redirects if directory doesn't exist)

So if the file EXISTS at /public_html/kusum/Whatsapp_Rem/frontend/index.php, it SHOULD be served directly.

Wait - the frontend/ dir has subdirectory .htaccess with the SAME rule. 
And our standalone_test.php returned index.php content too...

Actually the files DO exist on FTP, so the RewriteCond should prevent redirect.
The problem might be that the .htaccess in frontend/ is redirecting standalone_test.php to index.php 
because it doesn't exist as REQUEST_FILENAME. Let me check:
- standalone_test.php DOES exist as a file → should NOT be rewritten
- But we got index.php content back

This means:
1. Either frontend/ directory's index.php is still OLD (let me check sizes again)
2. OR there's an include/require chain

Let me check the actual file stored on FTP directly - and then check the __clear_cache.php
"""

import ftplib, sys, io, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Check file sizes on FTP
for path, fname in [
    ('/public_html', 'index.php'),
    ('/public_html/kusum', 'index.php'),
    ('/public_html/kusum/Whatsapp_Rem', 'index.php'),
    ('/public_html/kusum/Whatsapp_Rem/frontend', 'index.php'),
    ('/public_html/kusum/Whatsapp_Rem/frontend', 'standalone_test.php'),
]:
    try:
        size = ftp.size(f'{path}/{fname}')
        print(f"{path}/{fname}: {size} bytes")
    except Exception as e:
        print(f"{path}/{fname}: {e}")

# Read the __clear_cache.php content
try:
    buf = io.BytesIO()
    ftp.cwd('/public_html/kusum/Whatsapp_Rem')
    ftp.retrbinary('RETR __clear_cache.php', buf.write)
    print(f"\n__clear_cache.php content:\n{buf.getvalue().decode()}")
except Exception as e:
    print(f"__clear_cache.php: {e}")

# Read the .user.ini
try:
    buf = io.BytesIO()
    ftp.cwd('/public_html/kusum/Whatsapp_Rem')
    ftp.retrbinary('RETR .user.ini', buf.write)
    print(f"\n.user.ini content:\n{buf.getvalue().decode()}")
except Exception as e:
    print(f".user.ini: {e}")

ftp.quit()

# Test standalone_test.php directly with a unique cache-busting approach
time.sleep(1)
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/standalone_test.php'
req = urllib.request.Request(url, headers={
    'User-Agent': 'curl/7.68.0',  # Try different UA
    'Cache-Control': 'no-cache',
    'Accept': 'text/plain'
})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode('utf-8', errors='ignore')[:300]
        print(f"\nstandalone_test.php HTTP response (first 300 chars):")
        print(raw)
except Exception as e:
    print(f"Error: {e}")
