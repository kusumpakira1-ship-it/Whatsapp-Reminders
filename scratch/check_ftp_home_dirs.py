"""
IMPORTANT CHECK: The FTP root (home dir) has its own kusum/ and frontend/ directories.
If the web domain maps to the FTP HOME dir (not /public_html), then:
URL: /kusum/Whatsapp_Rem/frontend/index.php
maps to: ~/kusum/Whatsapp_Rem/frontend/index.php (NOT ~/public_html/kusum/...)

This would explain why our uploads to /public_html/... have no effect!
Let's check the FTP root's kusum/ directory structure.
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# The FTP root's kusum/ directory - NOT /public_html/kusum/
print("=== FTP ROOT's kusum/ directory ===")
try:
    ftp.cwd('/kusum')
    entries = []
    ftp.retrlines('LIST', entries.append)
    for e in entries:
        print(e)
except Exception as e:
    print(f"Error: {e}")

print("\n=== FTP ROOT's frontend/ directory ===")
try:
    ftp.cwd('/frontend')
    entries = []
    ftp.retrlines('LIST', entries.append)
    for e in entries:
        print(e)
except Exception as e:
    print(f"Error: {e}")

# Check the FTP root's .htaccess
print("\n=== FTP ROOT's .htaccess ===")
try:
    ftp.cwd('/')
    buf = io.BytesIO()
    ftp.retrbinary('RETR .htaccess', buf.write)
    print(buf.getvalue().decode('utf-8', errors='ignore'))
except Exception as e:
    print(f"Error: {e}")

ftp.quit()
