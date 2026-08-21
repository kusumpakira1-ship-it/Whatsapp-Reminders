"""
EVEN passthrough.php returns 197K. This is conclusive:
The /public_html/.htaccess is DEFINITELY intercepting ALL requests and redirecting 
them to /public_html/index.php BEFORE the child .htaccess files even run.

Evidence:
- Any URL under /kusum/Whatsapp_Rem/frontend/ returns the SAME 197K content
- Even files that don't exist return this same content
- Even after we updated the root .htaccess, it's still happening

This means our root .htaccess update may not have taken effect due to OPcache too.

THE NUCLEAR SOLUTION: 
We need Hostinger hPanel access to:
1. Go to Websites → Manage → Advanced → PHP configuration → Clear OPcache
OR
2. Go to Files → PHP config → Restart PHP workers

Since we can't do that programmatically, let me try:
1. Try Hostinger API for PHP restart
2. OR write a VERY SPECIFIC PHP file that accesses the Hostinger hPanel API

Actually - let me check if the .user.ini with opcache.enable=0 has taken effect by
testing if a simple PHP echo works. If it does, then the issue is purely about
WHICH FILE is being executed (the root index.php, not the frontend one).
"""

import ftplib, urllib.request, sys, io, time
sys.stdout.reconfigure(encoding='utf-8')

# Check the EXACT current content of /public_html/.htaccess
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

buf = io.BytesIO()
ftp.cwd('/public_html')
ftp.retrbinary('RETR .htaccess', buf.write)
print("Current /public_html/.htaccess:")
print(buf.getvalue().decode('utf-8', errors='ignore'))

# Check size of /public_html/index.php
buf2 = io.BytesIO()
ftp.retrbinary('RETR index.php', buf2.write)
root_content = buf2.getvalue().decode('utf-8', errors='ignore')
print(f"\n/public_html/index.php size: {len(root_content)}")
print(f"Has 'confirmToggleSubReport': {'YES' if 'confirmToggleSubReport' in root_content else 'NO'}")

ftp.quit()
