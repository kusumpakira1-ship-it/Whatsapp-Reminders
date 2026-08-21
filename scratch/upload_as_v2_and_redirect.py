"""
OPcache is DEFINITELY serving a cached/compiled version of index.php.
The .user.ini says opcache.enable=0 but this likely requires a PHP process restart to take effect.

The file on FTP is 239K (new), but PHP's OPcache has a compiled version of the OLD 197K file cached in memory.
Even opcache_reset() calls are being caught by .htaccess and served as index.php.

SOLUTION: Use Hostinger's file manager or SSH access to restart PHP-FPM,
OR trick OPcache by changing the file content checksum.

The key insight: opcache.revalidate_freq=0 in .user.ini means PHP should revalidate on EVERY request.
But it's not working. This suggests:
1. .user.ini requires web server restart to be read (PHP-FPM restarts the worker pool)
2. OR the opcache.enable=0 hasn't taken effect yet

ALTERNATIVE APPROACH: Upload index.php with a DIFFERENT name (e.g., index2.php) 
then update .htaccess to serve index2.php instead of index.php.
This forces OPcache to compile a NEW file (since it hasn't seen index2.php before).
"""

import ftplib, urllib.request, sys, io, time, shutil
sys.stdout.reconfigure(encoding='utf-8')

# Read the new local index.php
with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    new_code = f.read()

print(f"New index.php size: {len(new_code)} bytes")
print(f"Has confirmToggleSubReport: {'YES' if b'confirmToggleSubReport' in new_code else 'NO'}")

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Upload as a FRESH new filename: app_v2.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR app_v2.php', io.BytesIO(new_code))
print("Uploaded as app_v2.php in /public_html/kusum/Whatsapp_Rem/frontend")

# Update .htaccess to route to app_v2.php instead of index.php
new_htaccess = b"""RewriteEngine On
RewriteRule ^$ app_v2.php [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ app_v2.php [L]

<IfModule mod_headers.c>
    Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
</IfModule>
"""
ftp.storbinary('STOR .htaccess', io.BytesIO(new_htaccess))
print("Updated .htaccess to serve app_v2.php")

ftp.quit()

time.sleep(1)
# Test if the new file is served
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    has_toggle = 'confirmToggleSubReport' in html
    print(f"\nTest result from {url}:")
    print(f"  Size: {len(html)}")
    print(f"  Has 'confirmToggleSubReport': {'YES ✅' if has_toggle else 'NO ❌'}")
