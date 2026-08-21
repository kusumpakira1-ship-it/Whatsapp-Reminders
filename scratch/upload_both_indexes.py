"""
Copy frontend/index.php -> index.php and upload both to Hostinger FTP
"""

import ftplib, shutil, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

# Copy frontend/index.php to root index.php
shutil.copyfile(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php')
print("Copied frontend/index.php -> index.php cleanly!")

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php', 'rb') as f:
    file_bytes = f.read()

print(f"File size: {len(file_bytes)} bytes")

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Storing in /public_html/kusum/Whatsapp_Rem/frontend/index.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR index.php', io.BytesIO(file_bytes))
print("Stored index.php in /public_html/kusum/Whatsapp_Rem/frontend")

# Storing in /public_html/kusum/Whatsapp_Rem/index.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR index.php', io.BytesIO(file_bytes))
print("Stored index.php in /public_html/kusum/Whatsapp_Rem")

# Clear OPcache
clear_php = b"<?php opcache_reset(); echo 'OPCACHE_CLEARED_OK'; ?>"
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR oc_reset.php', io.BytesIO(clear_php))

ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR oc_reset.php', io.BytesIO(clear_php))

ftp.quit()
print("FTP uploads completed!")

# Clear via HTTP
import urllib.request
for u in ['https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/oc_reset.php', 'https://sunfragroup.com/kusum/Whatsapp_Rem/oc_reset.php']:
    try:
        res = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        print(f"Clear OPcache {u} => {urllib.request.urlopen(res, timeout=10).read().decode('utf-8')}")
    except Exception as e:
        print(f"Clear OPcache error {u}: {e}")

time.sleep(2)
# Check live HTML
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?nocache={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    has_func = 'confirmToggleSubReport' in html
    print(f"\nLive HTML Verification:")
    print(f"• Size: {len(html)} bytes")
    print(f"• Has confirmToggleSubReport? {'YES ✅' if has_func else 'NO ❌'}")
