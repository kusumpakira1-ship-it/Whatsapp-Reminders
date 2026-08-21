"""
THE REAL PATH: ~/kusum/Whatsapp_Rem/frontend/index.php (FTP home dir)
NOT: ~/public_html/kusum/Whatsapp_Rem/frontend/index.php

There's already clear_op.php in the correct directory!
Let's:
1. Check what clear_op.php contains
2. Check the parent .htaccess at ~/kusum/Whatsapp_Rem/.htaccess
3. Try accessing clear_op.php via HTTP
4. Upload our new index.php to the CORRECT path
5. Run opcache reset
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Read existing clear_op.php
try:
    ftp.cwd('/kusum/Whatsapp_Rem/frontend')
    buf = io.BytesIO()
    ftp.retrbinary('RETR clear_op.php', buf.write)
    print("clear_op.php content:")
    print(buf.getvalue().decode('utf-8', errors='ignore'))
except Exception as e:
    print(f"clear_op.php error: {e}")

# Read /kusum/Whatsapp_Rem/.htaccess
try:
    ftp.cwd('/kusum/Whatsapp_Rem')
    buf = io.BytesIO()
    ftp.retrbinary('RETR .htaccess', buf.write)
    print("\n/kusum/Whatsapp_Rem/.htaccess:")
    print(buf.getvalue().decode('utf-8', errors='ignore'))
except Exception as e:
    print(f".htaccess error: {e}")

# Read /kusum/.htaccess
try:
    ftp.cwd('/kusum')
    buf = io.BytesIO()
    ftp.retrbinary('RETR .htaccess', buf.write)
    print("\n/kusum/.htaccess:")
    print(buf.getvalue().decode('utf-8', errors='ignore'))
except Exception as e:
    print(f"/kusum/.htaccess error: {e}")

ftp.quit()

# Try accessing clear_op.php via HTTP
print("\n--- HTTP test of clear_op.php ---")
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/clear_op.php?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = resp.read().decode('utf-8', errors='ignore')
        print(f"Response size: {len(result)}")
        print(f"First 300 chars: {result[:300]}")
except Exception as e:
    print(f"HTTP error: {e}")
