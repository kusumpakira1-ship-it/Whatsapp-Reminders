"""
CRITICAL FINDING:
- The request IDs are all DIFFERENT (different CDN edge nodes: edge10, edge7, edge9)
- Cache status is DYNAMIC (PHP is executing fresh each time)
- Even POST returns 197K

This means PHP is actually RUNNING and producing the 197K output.
The FTP file is 239K but PHP produces 197K HTML output.
PHP OPcache is compiled the OLD version of the file.

The opcache_reset() in our .user.ini shows opcache.enable=0 - but this might not have been applied yet
to the PHP-FPM worker process pool. .user.ini changes require PHP process restart.

THE REAL FIX: We need to either:
1. SSH into the server and restart PHP-FPM 
2. OR use Hostinger's control panel to clear PHP cache
3. OR overwrite the compiled opcache file directly

BUT WAIT - let me re-read the output more carefully.
"x-hcdn-upstream-rt: 0.171" - this is 170ms upstream response time
"x-hcdn-cache-status: DYNAMIC" - this means it's bypassing cache, executing PHP

If PHP IS executing fresh (different edge nodes, different request IDs),
and the output is still 197K, then:
- Either PHP is executing a DIFFERENT physical file (not our 239K FTP file)
- OR PHP's OPcache compiled the old version and is using the compiled bytecode
  even though opcache.enable=0 is in .user.ini (which needs process restart)

SOLUTION APPROACH: Try to access the file's compiled opcache path directly and delete it,
OR use Hostinger's admin panel (hpanel.hostinger.com) to restart PHP.

For now, let me try another approach: 
Upload a PHP file that includes our code DYNAMICALLY to bypass OPcache:
"""

import ftplib, urllib.request, sys, io, time
sys.stdout.reconfigure(encoding='utf-8')

# Read the new code
with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    new_code = f.read()

# Strategy: Rename the OLD index.php -> index_old.php (to force OPcache miss)
# Then upload NEW content as index.php (fresh file, no compiled cache)
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')

# Delete old file first (forces opcache to lose the compiled entry)
try:
    ftp.delete('index.php')
    print("Deleted old index.php from FTP")
    time.sleep(1)
except Exception as e:
    print(f"Delete error: {e}")

# Re-upload fresh
ftp.storbinary('STOR index.php', io.BytesIO(new_code))
print("Re-uploaded fresh index.php")

# Also reset .htaccess back to serve index.php
htaccess = b"""RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [L]

<IfModule mod_headers.c>
    Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
</IfModule>
"""
ftp.storbinary('STOR .htaccess', io.BytesIO(htaccess))
print("Restored .htaccess to serve index.php")

ftp.quit()

time.sleep(3)
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?fresh={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    has_toggle = 'confirmToggleSubReport' in html
    print(f"\nAfter delete+reupload:")
    print(f"  Size: {len(html)}")
    print(f"  Has 'confirmToggleSubReport': {'YES ✅' if has_toggle else 'NO ❌'}")
