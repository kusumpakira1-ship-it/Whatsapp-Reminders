"""
Now we know:
- FTP Simple is connected to the FTP home dir (~/) NOT /public_html
- The website at /kusum/Whatsapp_Rem/frontend/ maps to /public_html/kusum/Whatsapp_Rem/frontend/
- We've been uploading to /public_html/kusum/Whatsapp_Rem/frontend/index.php which IS correct (239K)
- BUT the HTTP response is still 197K

The 197K could be coming from OPcache.
Let me try one final thing: read the EXACT 197K content's end, and search all FTP files for that exact ending.
Also try accessing via direct IP to bypass CDN.

KEY INSIGHT: The FTP root has /frontend/index.php and /index.php
The user's FTP Simple is browsing from ~ (home dir, NOT /public_html)
So when user edited the file in FTP Simple, they edited: ~/index.php (304K) NOT /public_html/kusum/Whatsapp_Rem/frontend/index.php

But WAIT - the diff showed file path is:
cedad10937994543724efa30b6e53514/index.php at ROOT of temp = FTP root's index.php

FTP root's index.php = 304110 bytes (very old, NOT our version)
The user saved to this file which maps to the FTP home root.

But HTTP still serves 197K...

Actually let me look at what URL maps to what FTP path:
- https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php
- = /public_html/kusum/Whatsapp_Rem/frontend/index.php on Hostinger

But due to /public_html/.htaccess redirecting all non-/kusum/ requests to /public_html/index.php...
Wait, we FIXED that. But OPcache still serves 197K.

Let me try looking at the actual FTP tree more carefully:
- FTP ~ (home) has: index.php (304K), frontend/, kusum/, public/, public_html/
- /public_html/ is INSIDE the home dir
- But http://sunfragroup.com/ maps to /public_html/ (Hostinger standard)

So the website URL /kusum/Whatsapp_Rem/frontend/index.php maps to:
/public_html/kusum/Whatsapp_Rem/frontend/index.php (which is 239K and correct!)

The 197K OPcache issue is the only explanation. The Hostinger PHP-FPM process must be restarted.

Let me try one more creative approach: trigger a PHP fatal error in a temp file to force 
PHP-FPM to respawn a worker process, which should load the new OPcache-disabled .user.ini.
"""
import ftplib, io, urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    new_code = f.read()

print(f"File to upload: {len(new_code)} bytes, has_toggle={b'confirmToggleSubReport' in new_code}")

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Upload the .user.ini with ALL opcache disabled to EVERY possible directory
user_ini = b"opcache.enable=0\nopcache.enable_cli=0\nopcache.revalidate_freq=0\nopcache.validate_timestamps=1\nopcache.max_wasted_percentage=5\n"

dirs = [
    '/public_html',
    '/public_html/kusum',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
]

for d in dirs:
    try:
        ftp.cwd(d)
        ftp.storbinary('STOR .user.ini', io.BytesIO(user_ini))
        # Also ensure our latest index.php is there
        ftp.storbinary('STOR index.php', io.BytesIO(new_code))
        print(f"Updated .user.ini + index.php in {d}")
    except Exception as e:
        print(f"Error {d}: {e}")

ftp.quit()

# Wait a few seconds then test
print("\nWaiting 5 seconds for PHP to pick up .user.ini changes...")
time.sleep(5)

for i in range(3):
    url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?attempt={i+1}&t={int(time.time())}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        has_toggle = 'confirmToggleSubReport' in html
        print(f"Attempt {i+1}: size={len(html)}, toggle={has_toggle}")
    time.sleep(2)
