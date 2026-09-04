import ftplib
import io
import sys
import urllib.request
import time

sys.stdout.reconfigure(encoding='utf-8')

htaccess_content = """# Disable Caching for PHP files on Hostinger CDN & LiteSpeed
<IfModule mod_headers.c>
    Header always set Cache-Control "no-store, no-cache, must-revalidate, max-age=0, s-maxage=0"
    Header always set Pragma "no-cache"
    Header always set Expires "0"
    Header always set X-Hostinger-CDN-Cache "bypass"
    Header always set CDN-Cache-Control "no-store"
    Header always set X-LiteSpeed-Cache-Control "no-cache, no-store, must-revalidate"
    Header always set X-LiteSpeed-Purge "*"
</IfModule>

<IfModule mod_expires.c>
    ExpiresActive Off
</IfModule>

<FilesMatch "\\.(php)$">
    <IfModule mod_headers.c>
        Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0, s-maxage=0"
        Header set X-Hostinger-CDN-Cache "bypass"
        Header set CDN-Cache-Control "no-store"
        Header set X-LiteSpeed-Cache-Control "no-cache, no-store, must-revalidate"
    </IfModule>
</FilesMatch>
""".encode('utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

htaccess_paths = [
    '/public_html/.htaccess',
    '/public_html/kusum/.htaccess',
    '/public_html/kusum/Whatsapp_Rem/.htaccess',
    '/public_html/kusum/Whatsapp_Rem/frontend/.htaccess'
]

for hp in htaccess_paths:
    try:
        ftp.storbinary(f'STOR {hp}', io.BytesIO(htaccess_content))
        print(f"Updated {hp}")
    except Exception as e:
        print(f"Failed {hp}: {e}")

ftp.quit()

print("\n--- TRIGGERING PURGE HEADERS ---")
req = urllib.request.Request("https://sunfragroup.com/kusum/Whatsapp_Rem/index.php", headers={
    'User-Agent': 'Mozilla/5.0',
    'X-LiteSpeed-Purge': '*',
    'Cache-Control': 'no-cache, no-store, must-revalidate'
})

try:
    with urllib.request.urlopen(req, timeout=10) as res:
        print("Purge GET response status:", res.status)
except Exception as e:
    print("Purge GET error:", e)

time.sleep(2)

print("\n--- RE-TESTING MAIN URL ---")
req2 = urllib.request.Request("https://sunfragroup.com/kusum/Whatsapp_Rem/index.php", headers={
    'User-Agent': 'Mozilla/5.0',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
})

try:
    with urllib.request.urlopen(req2, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Main URL HTTP Length: {len(html)} bytes")
        has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
        has_mon_fri = 'value="mon-fri"' in html or 'Mon to Fri' in html
        print(f"Contains 'Mon to Sat': {has_mon_sat}")
        print(f"Contains 'Mon to Fri': {has_mon_fri}")
except Exception as e:
    print("Main URL fetch error:", e)
