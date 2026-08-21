"""
EVEN a brand new file (rem_XXXX.php) returns 197149 bytes - the old content.
This means the .htaccess redirect IS catching everything and serving it through index.php (old version).

The frontend/.htaccess does:
RewriteCond %{REQUEST_FILENAME} !-f  
RewriteRule ^(.*)$ index.php [L]

But rem_1786612843.php DOES exist as a file on FTP...
Unless Hostinger's REQUEST_FILENAME is resolving differently.

Wait - maybe the PARENT .htaccess at /public_html/.htaccess is catching FIRST.
In Apache, parent .htaccess files run before child ones in some configurations.

The /public_html/.htaccess:
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f  -- CHECK: Is /public_html/kusum/Whatsapp_Rem/frontend/rem_XXX.php a REAL FILE from Apache's perspective?
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [L]

Apache's REQUEST_FILENAME in /public_html/.htaccess context maps to:
/public_html + /kusum/Whatsapp_Rem/frontend/rem_XXX.php = correct path

Hmm, the file exists, so it shouldn't redirect.

ALTERNATIVE THEORY: The Hostinger hpanel for this account has a different document root 
or there's a PHP include in /public_html/index.php that includes another file.

Let me check if the HTTP response HTML has any PHP-generated markers (like __FILE__ output)
that could tell us which file is actually being executed.
"""
import urllib.request, sys, io, ftplib, time
sys.stdout.reconfigure(encoding='utf-8')

# Upload a small debug file that reveals itself
debug_php = b"""<?php
header('Content-Type: text/plain');
echo 'EXECUTED_FILE: ' . __FILE__ . "\\n";
echo 'DOC_ROOT: ' . $_SERVER['DOCUMENT_ROOT'] . "\\n";
echo 'SCRIPT_FILENAME: ' . $_SERVER['SCRIPT_FILENAME'] . "\\n";
echo 'PHP_SELF: ' . $_SERVER['PHP_SELF'] . "\\n";
echo 'REQUEST_URI: ' . $_SERVER['REQUEST_URI'] . "\\n";
echo 'PHP_VERSION: ' . PHP_VERSION . "\\n";
echo 'TIMESTAMP: ' . time() . "\\n";
"""

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# REMOVE the .htaccess from frontend temporarily to stop the redirect
# Then upload our debug file
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')

# Rename (backup) the .htaccess
try:
    ftp.rename('.htaccess', '.htaccess_backup')
    print("Backed up .htaccess to .htaccess_backup")
except Exception as e:
    print(f"Backup .htaccess: {e}")

# Upload debug file
ftp.storbinary('STOR debug_me.php', io.BytesIO(debug_php))
print("Uploaded debug_me.php")

ftp.quit()

time.sleep(1)
url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/debug_me.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = resp.read().decode('utf-8', errors='ignore')
        print(f"\ndebug_me.php response:")
        print(result)
except Exception as e:
    print(f"Error: {e}")
