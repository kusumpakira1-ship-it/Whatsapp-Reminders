"""
Test API endpoints to determine cache type:
- If JSON API works/returns live data → PHP executes fresh (OPcache issue for specific file)
- If JSON API is also stale/broken → LiteSpeed full-page cache (affects ALL responses)

Also try LiteSpeed-specific cache disable headers in .htaccess
"""
import ftplib, io, sys, urllib.request, time, json
sys.stdout.reconfigure(encoding='utf-8')

# Test 1: Try API endpoint with ?action=getGroups
print("=== Test 1: API Endpoint Test ===")
for action in ['getGroups', 'getReminders', 'getWahaStatus']:
    url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?action={action}&t={int(time.time())}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            is_json = content.strip().startswith('{') or content.strip().startswith('[')
            print(f"  ?action={action}: size={len(content)}, is_json={is_json}")
            if is_json:
                print(f"    JSON response (PHP IS executing fresh): {content[:100]}")
    except Exception as e:
        print(f"  ?action={action}: Error {e}")

# Test 2: Try the standalone_test.php that was there earlier
print("\n=== Test 2: standalone_test.php ===")
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/standalone_test.php?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8', errors='ignore')
        print(f"  Size: {len(content)}, is_197K: {len(content)==197149}")
        print(f"  First 100: {content[:100]}")
except Exception as e:
    print(f"  Error: {e}")

# Test 3: Upload .htaccess with LiteSpeed-specific cache disable to CORRECT path
print("\n=== Test 3: LiteSpeed Cache Disable via .htaccess ===")
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ls_htaccess = b"""<IfModule LiteSpeed>
    CacheLookup off
</IfModule>
<IfModule mod_lsapi.c>
    php_value opcache.enable 0
    php_value opcache.validate_timestamps 1
    php_value opcache.revalidate_freq 0
</IfModule>
<IfModule mod_headers.c>
    Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
    Header set X-LiteSpeed-Cache-Control "no-cache"
    Header set X-LiteSpeed-Purge "*"
</IfModule>
"""

for d in ['/public_html/kusum/Whatsapp_Rem/frontend', '/kusum/Whatsapp_Rem/frontend']:
    try:
        ftp.cwd(d)
        ftp.storbinary('STOR .htaccess', io.BytesIO(ls_htaccess))
        print(f"  Uploaded LiteSpeed cache-off .htaccess to {d}")
    except Exception as e:
        print(f"  Error {d}: {e}")

ftp.quit()

time.sleep(2)
url3 = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?nocache={int(time.time())}'
req3 = urllib.request.Request(url3, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
with urllib.request.urlopen(req3, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print(f"\n  After LiteSpeed cache-off: size={len(html)}, toggle={'confirmToggleSubReport' in html}")
