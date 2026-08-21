"""
Key finding: standalone_test.php EXISTS on FTP but returns index.php HTML content.
This means the .htaccess RewriteCond %{REQUEST_FILENAME} !-f is NOT working as expected.
The file exists as a real file but Apache still rewrites it to index.php.

This happens when:
1. The AllowOverride is not set properly (unlikely on Hostinger)
2. The RewriteBase is wrong
3. There's a PARENT .htaccess that's overriding BEFORE the child one applies

Looking at /public_html/.htaccess:
RewriteRule ^(.*)$ index.php [L]
This has NO conditions! It matches EVERYTHING including existing files.

Since /public_html/.htaccess has NO RewriteCond, it redirects EVERYTHING including:
- /public_html/kusum/Whatsapp_Rem/frontend/standalone_test.php 
to /public_html/index.php (197149 bytes - the old file!)

FIX: We need to update /public_html/index.php with our new code,
OR add conditions to /public_html/.htaccess to exclude /kusum/ paths,
OR upload our new index.php to /public_html/index.php

Let's check what's in /public_html/index.php to understand if it's the same app
"""

import ftplib, sys, io
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)
ftp.set_pasv(True)

# Read the first 5000 bytes of /public_html/index.php
buf = io.BytesIO()
ftp.cwd('/public_html')
ftp.retrbinary('RETR index.php', buf.write, blocksize=8192)
content = buf.getvalue().decode('utf-8', errors='ignore')
print(f"Total /public_html/index.php size: {len(content)} chars")
print(f"\nFirst 2000 chars:")
print(content[:2000])
print(f"\nHas 'confirmToggleSubReport': {'YES' if 'confirmToggleSubReport' in content else 'NO'}")
ftp.quit()
