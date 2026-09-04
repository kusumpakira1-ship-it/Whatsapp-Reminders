import ftplib
import io
import sys
import urllib.request
import time

sys.stdout.reconfigure(encoding='utf-8')

htaccess_content = """<IfModule mod_headers.c>
    Header set Cache-Control "private, no-cache, no-store, must-revalidate, max-age=0, s-maxage=0, post-check=0, pre-check=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
    Header set X-Hostinger-CDN-Cache "bypass"
    Header set CDN-Cache-Control "no-store"
    Header set X-LiteSpeed-Cache-Control "no-cache, no-store, must-revalidate"
    Header set X-LiteSpeed-Purge "*"
</IfModule>

<IfModule mod_expires.c>
    ExpiresActive Off
</IfModule>
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
        print(f"Updated .htaccess -> {hp}")
    except Exception as e:
        print(f"Failed .htaccess {hp}: {e}")

ftp.quit()

print("\n--- SENDING PURGE REQUESTS TO HOSTINGER CDN ---")
endpoints = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/clear_cache.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?purge=1",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php"
]

for ep in endpoints:
    try:
        req = urllib.request.Request(ep, headers={
            'User-Agent': 'Mozilla/5.0',
            'X-LiteSpeed-Purge': '*',
            'Cache-Control': 'no-cache, no-store, must-revalidate'
        })
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"Purge request {ep} status: {res.status}")
    except Exception as e:
        print(f"Purge request {ep} error: {e}")

time.sleep(3)

print("\n--- RE-TESTING LIVE WEBSITE HTTP ---")
req = urllib.request.Request(f"https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?t={time.time()}", headers={
    'User-Agent': 'Mozilla/5.0',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Fetched HTML Length: {len(html)} bytes")
        has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
        has_mon_fri = 'value="mon-fri"' in html or 'Mon to Fri' in html
        print(f"Contains 'Mon to Sat': {has_mon_sat}")
        print(f"Contains 'Mon to Fri': {has_mon_fri}")
except Exception as e:
    print(f"Verification error: {e}")
