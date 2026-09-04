import ftplib
import io
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

htaccess_content = """# Hostinger CDN Bypass Rewrite Rule
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteRule ^index\\.php$ index1.php [L]
</IfModule>

<IfModule mod_headers.c>
    Header always set Cache-Control "no-store, no-cache, must-revalidate, max-age=0, s-maxage=0"
    Header always set Pragma "no-cache"
    Header always set Expires "0"
    Header always set X-Hostinger-CDN-Cache "bypass"
    Header always set CDN-Cache-Control "no-store"
    Header always set X-LiteSpeed-Cache-Control "no-cache, no-store, must-revalidate"
    Header always set X-LiteSpeed-Purge "*"
</IfModule>
""".encode('utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

target_htaccess = '/public_html/kusum/Whatsapp_Rem/.htaccess'
ftp.storbinary(f'STOR {target_htaccess}', io.BytesIO(htaccess_content))
ftp.quit()

print("Uploaded rewrite rule to .htaccess")

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"URL: {url} -> len={len(html)}")
        has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
        has_mon_fri = 'value="mon-fri"' in html or 'Mon to Fri' in html
        print(f"Contains 'Mon to Sat': {has_mon_sat}")
        print(f"Contains 'Mon to Fri': {has_mon_fri}")
        if has_mon_sat and has_mon_fri:
            print("REWRITE BYPASS WORKED PERFECTLY!")
except Exception as e:
    print(f"Error fetching {url}: {e}")
