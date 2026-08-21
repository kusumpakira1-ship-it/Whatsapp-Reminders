"""
Update all .htaccess files on FTP with aggressive Hostinger CDN bypass headers.
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

ht_content = b"""<IfModule mod_headers.c>
    Header set Cache-Control "private, no-cache, no-store, must-revalidate, max-age=0, s-maxage=0, post-check=0, pre-check=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
    Header set X-Hostinger-CDN-Cache "bypass"
    Header set CDN-Cache-Control "no-store"
    Header set X-LiteSpeed-Cache-Control "no-cache"
    Header set X-LiteSpeed-Purge "*"
</IfModule>
"""

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

paths = [
    '/',
    '/public_html',
    '/public_html/kusum',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/kusum',
    '/kusum/Whatsapp_Rem',
    '/kusum/Whatsapp_Rem/frontend'
]

for p in paths:
    try:
        ftp.cwd(p)
        ftp.storbinary('STOR .htaccess', io.BytesIO(ht_content))
        print(f"Uploaded CDN bypass .htaccess to {p} ✅")
    except Exception as e:
        print(f"Failed {p}: {e}")

ftp.quit()

time.sleep(2)

# Test live URL
url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?t={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"\nLive HTTP Test:")
        print(f"  Size: {len(html)} bytes")
        print(f"  Has 'confirmToggleSubReport': {'confirmToggleSubReport' in html}")
        print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
except Exception as e:
    print(f"Error: {e}")

