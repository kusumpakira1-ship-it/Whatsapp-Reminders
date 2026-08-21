"""
DEFINITIVE FIX:
The /public_html/.htaccess intercepts ALL requests with RewriteRule ^(.*)$ index.php [L]
(the RewriteCond checks are there but Apache's REQUEST_FILENAME from /public_html perspective 
might not resolve the subdirectory files correctly with the parent htaccess).

APPROACH: 
1. Fix /public_html/.htaccess to NOT redirect /kusum/ paths
2. Also update /public_html/index.php with our new code (belt+suspenders)

Let me fix the root htaccess to exclude /kusum/ subdirectory.
"""
import ftplib, urllib.request, sys, io, time
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    new_code = f.read()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Fix the ROOT .htaccess to NOT intercept /kusum/ paths
root_htaccess = b"""RewriteEngine On

# DO NOT redirect /kusum/ subdirectory - it has its own routing
RewriteCond %{REQUEST_URI} ^/kusum/ [NC]
RewriteRule .* - [L]

# For root domain requests, redirect to index.php
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [L]

<IfModule mod_headers.c>
    Header set Cache-Control "no-cache, no-store, must-revalidate, max-age=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
</IfModule>
"""
ftp.cwd('/public_html')
ftp.storbinary('STOR .htaccess', io.BytesIO(root_htaccess))
print("Updated /public_html/.htaccess to exclude /kusum/ paths ✅")

# Also update /public_html/index.php with the new code (in case it's still needed)
ftp.storbinary('STOR index.php', io.BytesIO(new_code))
print(f"Updated /public_html/index.php ({len(new_code)} bytes) ✅")

# Restore frontend .htaccess from backup
try:
    ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
    ftp.rename('.htaccess_backup', '.htaccess')
    print("Restored /public_html/kusum/Whatsapp_Rem/frontend/.htaccess ✅")
except Exception as e:
    print(f"Restore .htaccess: {e}")
    # Upload fresh htaccess
    ht = b"""RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [L]

<IfModule mod_headers.c>
    Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
</IfModule>
"""
    ftp.storbinary('STOR .htaccess', io.BytesIO(ht))
    print("Uploaded fresh .htaccess ✅")

ftp.quit()

time.sleep(2)
# Test
for url_path in [
    '/kusum/Whatsapp_Rem/frontend/index.php',
    '/kusum/Whatsapp_Rem/frontend/debug_me.php',
]:
    url = f'https://sunfragroup.com{url_path}?t={int(time.time())}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            has_toggle = 'confirmToggleSubReport' in html
            print(f"\n{url_path}:")
            print(f"  Size: {len(html)}")
            print(f"  Has 'confirmToggleSubReport': {'YES ✅' if has_toggle else 'NO ❌'}")
            print(f"  First 200 chars: {html[:200]}")
    except Exception as e:
        print(f"Error {url_path}: {e}")
