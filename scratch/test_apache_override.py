"""
Inject X-Debug-Build header into .htaccess on Hostinger FTP to test Apache execution
"""

import ftplib, urllib.request, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

ht_content = b"""RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [L]

<IfModule mod_headers.c>
    Header set X-Debug-Build "BUILD_999"
    Header set Cache-Control "no-cache, no-store, must-revalidate, max-age=0"
</IfModule>
"""

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR .htaccess', io.BytesIO(ht_content))
print("Stored modified .htaccess in /public_html/kusum/Whatsapp_Rem/frontend")

ftp.quit()

time.sleep(1)
url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        headers = dict(resp.headers)
        print("Response Headers:")
        for k, v in headers.items():
            print(f" {k}: {v}")
except Exception as e:
    print("Error:", e)
