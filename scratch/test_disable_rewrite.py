"""
Disable mod_rewrite and LiteSpeed cache in frontend/.htaccess and test index.php output!
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

htaccess_code = b"""<IfModule mod_rewrite.c>
    RewriteEngine Off
</IfModule>
<IfModule LiteSpeed>
    CacheLookup off
</IfModule>
<IfModule mod_headers.c>
    Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0, s-maxage=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
    Header set X-LiteSpeed-Cache-Control "no-cache"
    Header set X-LiteSpeed-Purge "*"
    Header set X-Hostinger-CDN-Cache "bypass"
</IfModule>
"""

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

paths = [
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/kusum/Whatsapp_Rem/frontend'
]

for p in paths:
    try:
        ftp.cwd(p)
        ftp.storbinary('STOR .htaccess', io.BytesIO(htaccess_code))
        print(f"Uploaded rewrite-disabled .htaccess to {p} ✅")
    except Exception as e:
        print(f"Failed {p}: {e}")

ftp.quit()

time.sleep(1)

test_url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?t={int(time.time())}"
try:
    req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"\nLive HTTP Test frontend/index.php:")
        print(f"  Status: {resp.status}, Size: {len(html)} bytes")
        print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
        print(f"  Has 'changeRemindersViewingDate': {'changeRemindersViewingDate' in html}")
        print(f"  Has 'sub_reports_status': {'sub_reports_status' in html}")
except Exception as e:
    print("Error:", e)

