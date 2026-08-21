"""
Check server headers to determine web server type (Nginx/Apache/LiteSpeed)
Then try php_value auto_prepend_file via .htaccess (works on Apache/LiteSpeed)
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

# Check server headers
url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    print("=== Response Headers ===")
    for k, v in resp.headers.items():
        print(f"  {k}: {v}")
    _ = resp.read()

print()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Upload a .htaccess with auto_prepend_file to the correct directory
# This works on Apache mod_php AND LiteSpeed
auto_prepend_htaccess = b"""<IfModule mod_php.c>
php_value auto_prepend_file /home/u632391467/kusum/Whatsapp_Rem/frontend/clear_op.php
</IfModule>
<IfModule lsapi_module>
php_value auto_prepend_file /home/u632391467/kusum/Whatsapp_Rem/frontend/clear_op.php
</IfModule>
"""

ftp.cwd('/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR .htaccess', io.BytesIO(auto_prepend_htaccess))
print("Uploaded .htaccess with auto_prepend_file for opcache_reset ✅")
ftp.quit()

time.sleep(1)
# Access index.php - if auto_prepend works, clear_op.php will run first
print("Accessing index.php to trigger opcache_reset via auto_prepend_file...")
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?reset={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    has_toggle = 'confirmToggleSubReport' in html
    has_reset_ok = 'OPCACHE_CLEARED_OK' in html
    print(f"Size: {len(html)}, has_toggle={has_toggle}, has_reset_echo={has_reset_ok}")
    if has_reset_ok:
        print("OPcache was cleared! Requesting again...")
        time.sleep(1)
        req2 = urllib.request.Request(url + '2', headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req2, timeout=15) as r2:
            html2 = r2.read().decode('utf-8', errors='ignore')
            print(f"Second request: size={len(html2)}, toggle={'confirmToggleSubReport' in html2}")
