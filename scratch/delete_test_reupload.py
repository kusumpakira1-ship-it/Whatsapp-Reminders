"""
DEFINITIVE TEST: Delete index.php from the correct FTP path.
If HTTP response changes (404 or error), then the web server IS serving from FTP.
If HTTP response stays 197K, then it's serving from somewhere else.
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    new_code = f.read()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# First restore .htaccess to something minimal (no auto_prepend)
minimal_ht = b"""<IfModule mod_headers.c>
    Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
</IfModule>
"""
ftp.cwd('/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR .htaccess', io.BytesIO(minimal_ht))
print("Restored minimal .htaccess")

# DELETE index.php
try:
    ftp.delete('index.php')
    print("DELETED index.php from ~/kusum/Whatsapp_Rem/frontend/")
except Exception as e:
    print(f"Delete error: {e}")

ftp.quit()

time.sleep(1)

# Test HTTP response
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        status = resp.status
        print(f"\nAfter DELETE: HTTP {status}, size={len(html)}")
        print(f"Still 197K: {len(html) == 197149}")
        print(f"First 100 chars: {html[:100]}")
except urllib.error.HTTPError as e:
    print(f"\nAfter DELETE: HTTP Error {e.code} - {e.reason}")
    print("✅ This means server IS reading from FTP! File not found = correct path confirmed")
except Exception as e:
    print(f"\nAfter DELETE: {e}")

# Re-upload our new code
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)
ftp.cwd('/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR index.php', io.BytesIO(new_code))
print(f"\nRe-uploaded new index.php ({len(new_code)} bytes)")
ftp.quit()

time.sleep(2)
# Test again
url2 = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?fresh={int(time.time())}'
req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req2, timeout=15) as resp:
    html2 = resp.read().decode('utf-8', errors='ignore')
    print(f"\nAfter re-upload: size={len(html2)}, toggle={'confirmToggleSubReport' in html2}")
