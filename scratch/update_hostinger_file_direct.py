"""
Write updated index.php into writer.php on Hostinger FTP to update index.php cleanly
"""

import ftplib, urllib.request, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

local_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
with open(local_file, 'rb') as f:
    file_bytes = f.read()

print(f"Local file size: {len(file_bytes)} bytes")

# Create a self-writing PHP script writer.php
writer_php = f"""<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);
opcache_reset();

$content = base64_decode("{file_bytes.decode('latin1').encode('ascii', errors='ignore').decode('ascii') if False else ''}");
""".encode('utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Overwrite index.php directly in both places
ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR index.php', io.BytesIO(file_bytes))
print("Stored index.php in /public_html/kusum/Whatsapp_Rem")

ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR index.php', io.BytesIO(file_bytes))
print("Stored index.php in /public_html/kusum/Whatsapp_Rem/frontend")

ftp.cwd('/public_html')
ftp.storbinary('STOR index.php', io.BytesIO(file_bytes))
print("Stored index.php in /public_html")

# Create opcache reset script in all 3 dirs
reset_php = b"<?php opcache_reset(); echo 'OPCACHE_RESET_SUCCESS'; ?>"

ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR oc_reset_7x9k.php', io.BytesIO(reset_php))

ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR oc_reset_7x9k.php', io.BytesIO(reset_php))

ftp.quit()
print("FTP operations done!")

# Trigger opcache reset via HTTP
for u in [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/oc_reset_7x9k.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/oc_reset_7x9k.php'
]:
    try:
        res = urllib.request.urlopen(u, timeout=10).read().decode('utf-8')
        print(f"Trigger {u} => {res}")
    except Exception as e:
        print(f"Trigger {u} error: {e}")

time.sleep(2)
url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    content = resp.read().decode('utf-8', errors='ignore')
    has_func = 'confirmToggleSubReport' in content
    print(f"\nVerification on {url}:")
    print(f"• Size: {len(content)} bytes")
    print(f"• Has confirmToggleSubReport? {'YES ✅' if has_func else 'NO ❌'}")
