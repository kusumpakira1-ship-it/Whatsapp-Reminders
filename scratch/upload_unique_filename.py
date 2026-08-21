"""
The PHP OPcache is truly stuck with the old 197K compiled bytecode.
Even after deleting and re-uploading index.php, the compiled opcache still serves the old version.

The ONLY reliable way to fix this without SSH/panel access is:
1. Upload a completely DIFFERENT filename that has never been compiled before
2. Make it the entry point

But our .htaccess redirect is also being rewritten...

Wait - let me check something. When we access index.php directly (not through .htaccess rewrite),
what happens? What if we try accessing the file with a query string or URL that makes Apache
serve the file directly without .htaccess involvement?

Actually, the correct URL is:
https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php

This DIRECTLY accesses the index.php file. The .htaccess RewriteCond %{REQUEST_FILENAME} !-f
means "if the file does NOT exist, redirect". Since index.php DOES exist, it should NOT redirect.
So index.php is being EXECUTED directly.

The OPcache is caching the COMPILED PHP bytecode of the old index.php.
When we upload a new file via FTP, the opcache still has the old compiled version in memory.
.user.ini opcache.enable=0 won't take effect until PHP process restart.

CRITICAL QUESTION: Are we uploading to the RIGHT path?
Let me check: what is the DOCUMENT ROOT of the Hostinger server?

If the domain sunfragroup.com maps to /public_html, then:
URL: /kusum/Whatsapp_Rem/frontend/index.php
Physical file: /public_html/kusum/Whatsapp_Rem/frontend/index.php ✓

But we know OPcache has cached the 197K version. 

The ONLY solution now: 
- Try to access Hostinger hPanel to clear PHP cache / restart PHP workers
- OR find a file that CAN be executed as fresh PHP without opcache

Let me try one more thing: upload the file with a TIMESTAMP name like index_20260813.php
and access THAT URL directly - bypassing .htaccess since the file exists.
"""
import ftplib, urllib.request, sys, io, time
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    new_code = f.read()

ts = int(time.time())
new_fname = f'rem_{ts}.php'

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary(f'STOR {new_fname}', io.BytesIO(new_code))
print(f"Uploaded {new_fname} ({len(new_code)} bytes)")
ftp.quit()

time.sleep(1)
# Access the unique filename directly (NEVER been opcached)
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/{new_fname}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    has_toggle = 'confirmToggleSubReport' in html
    print(f"\nDirect access to {new_fname}:")
    print(f"  Size: {len(html)}")
    print(f"  Has 'confirmToggleSubReport': {'YES ✅' if has_toggle else 'NO ❌'}")
    print(f"\n  NEW URL for you to use: https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/{new_fname}")
