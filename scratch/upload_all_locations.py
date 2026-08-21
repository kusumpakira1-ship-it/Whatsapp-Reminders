"""
Upload updated frontend/index.php and index.php to Hostinger FTP and clear OPcache
"""

import ftplib, urllib.request, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

local_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
with open(local_file, 'rb') as f:
    file_bytes = f.read()

print(f"Local file size: {len(file_bytes)} bytes")

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

clear_php = b"<?php opcache_reset(); echo 'OPCACHE_CLEARED_OK'; ?>"

dirs = ['/kusum/Whatsapp_Rem/frontend', '/kusum/Whatsapp_Rem']
for d in dirs:
    try:
        ftp.cwd(d)
        ftp.storbinary('STOR index.php', io.BytesIO(file_bytes))
        ftp.storbinary('STOR clear_op.php', io.BytesIO(clear_php))
        print(f"Successfully stored index.php & clear_op.php in {d}")
    except Exception as e:
        print(f"Error storing in {d}: {e}")

ftp.quit()

# Call clear_op.php to clear OPcache
time.sleep(1)
for d_url in ['https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/clear_op.php', 'https://sunfragroup.com/kusum/Whatsapp_Rem/clear_op.php']:
    try:
        req = urllib.request.Request(d_url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Clear OPcache URL {d_url} => {resp.read().decode('utf-8')}")
    except Exception as e:
        print(f"Clear OPcache URL {d_url} error: {e}")

# Verify live index.php
time.sleep(1)
urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/index.php'
]
for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            has_func = 'confirmToggleSubReport' in content
            print(f"URL: {url} -> Size: {len(content)} bytes -> Has confirmToggleSubReport? {'YES ✅' if has_func else 'NO ❌'}")
    except Exception as e:
        print(f"URL {url} check error: {e}")
