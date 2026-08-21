"""
Completely different approach: The 197K content is being served persistently from SOMEWHERE.
Let me check: what if there's a load balancer / reverse proxy at Hostinger level 
that has its own cache and it's serving the old cached output?

The hcdn (Hostinger CDN) shows x-hcdn-cache-status: DYNAMIC which means the CDN
is not caching - it fetches fresh from origin. But the ORIGIN is serving 197K.

The origin is a PHP-FPM process. PHP-FPM might have:
1. Cached the PHP bytecode in OPcache
2. OR there's a PHP output buffer cached somewhere

Since opcache.enable=0 is in .user.ini but the old version still serves...
This could mean PHP-FPM process hasn't restarted to pick up the .user.ini changes.

THE NUCLEAR OPTION: Upload a PHP file that directly does `file_get_contents` of our index.php
and outputs it. This bypasses OPcache because we're reading and echoing the file, not executing it.

Wait - actually a BETTER approach:
Upload our new code as a .txt file (no PHP execution), then use another PHP to include() it.

OR: Use eval() to run the code from a freshly-read file.

Actually the SIMPLEST approach I haven't tried:
Check if there's already a working URL that doesn't go through the hcdn CDN.
Hostinger has the real server IP. If we bypass the CDN...
"""
import ftplib, urllib.request, sys, io, time
sys.stdout.reconfigure(encoding='utf-8')

# Strategy: Upload a .php file that reads index.php as text and echoes it
# This bypasses PHP OPcache since we're doing file_get_contents not include/require
passthrough_php = b"""<?php
// Direct file output - bypasses OPcache by reading file as text and eval'ing it
$file = __DIR__ . '/index.php';
$code = file_get_contents($file);
// Remove the opening PHP tag
$code = preg_replace('/^<\\?php\\s*/', '', $code, 1);
eval($code);
?>"""

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR passthrough.php', io.BytesIO(passthrough_php))
print("Uploaded passthrough.php")
ftp.quit()

time.sleep(1)
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/passthrough.php?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        has_toggle = 'confirmToggleSubReport' in html
        print(f"\npassthrough.php result:")
        print(f"  Size: {len(html)}")
        print(f"  Has 'confirmToggleSubReport': {'YES ✅' if has_toggle else 'NO ❌'}")
        if has_toggle:
            print(f"\n  WORKING URL: {url}")
except Exception as e:
    print(f"Error: {e}")
