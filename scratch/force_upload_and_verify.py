"""
Force upload frontend/index.php to both Hostinger locations and reset OPcache
"""

import ftplib, shutil, sys, time, io, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

# Ensure root index.php is identical to frontend/index.php
shutil.copyfile(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php')
print("1. Synchronized local frontend/index.php -> index.php")

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    code = f.read()

print(f"2. File size to upload: {len(code)} bytes")

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Path 1: /public_html/kusum/Whatsapp_Rem/frontend/index.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR index.php', io.BytesIO(code))
print("3. Uploaded to /public_html/kusum/Whatsapp_Rem/frontend/index.php ✅")

# Path 2: /public_html/kusum/Whatsapp_Rem/index.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR index.php', io.BytesIO(code))
print("4. Uploaded to /public_html/kusum/Whatsapp_Rem/index.php ✅")

# Upload OPcache reset script
opcache_php = b"<?php opcache_reset(); clearstatcache(true); echo 'OPCACHE_RESET_SUCCESS'; ?>"
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR reset_opcache.php', io.BytesIO(opcache_php))
ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR reset_opcache.php', io.BytesIO(opcache_php))

ftp.quit()
print("5. FTP Upload Completed Successfully!")

# Trigger OPcache Reset via HTTP
for url in [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/reset_opcache.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/reset_opcache.php'
]:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        res = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        print(f"6. HTTP OPcache reset ({url}): {res}")
    except Exception as e:
        print(f"6. HTTP OPcache reset ({url}) error: {e}")

time.sleep(1)

# Verify HTTP response for presence of sub_report_status
test_url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?v={int(time.time())}"
req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print(f"\n7. Live Server Response Verification:")
    print(f"• URL: {test_url}")
    print(f"• Size: {len(html)} bytes")
    print(f"• Has 'confirmToggleSubReport'? {'YES ✅' if 'confirmToggleSubReport' in html else 'NO ❌'}")
    print(f"• Has 'sub_reports_status'? {'YES ✅' if 'sub_reports_status' in html else 'NO ❌'}")
