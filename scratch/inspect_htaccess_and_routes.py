import ftplib
import sys
import urllib.request
import re

sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("=== 1. CHECKING ALL .HTACCESS FILES ON FTP ===")
htaccess_paths = [
    '/public_html/.htaccess',
    '/public_html/kusum/.htaccess',
    '/public_html/kusum/Whatsapp_Rem/.htaccess',
    '/public_html/kusum/Whatsapp_Rem/frontend/.htaccess'
]

for hp in htaccess_paths:
    try:
        import io
        buf = io.BytesIO()
        ftp.retrbinary(f'RETR {hp}', buf.write)
        content = buf.getvalue().decode('utf-8', errors='ignore')
        print(f"\n--- {hp} ---")
        print(content)
    except Exception as e:
        print(f"\n--- {hp} --- (not found or error: {e})")

print("\n=== 2. LISTING ALL FILES IN /public_html/kusum/Whatsapp_Rem/ ===")
items = []
try:
    ftp.retrlines('LIST /public_html/kusum/Whatsapp_Rem/', items.append)
    for item in items:
        print(item)
except Exception as e:
    print(f"Error listing dir: {e}")

ftp.quit()

print("\n=== 3. ANALYZING HTTP RESPONSE HEADERS & SERVED FILE ===")
req = urllib.request.Request("https://sunfragroup.com/kusum/Whatsapp_Rem/index.php", headers={
    'User-Agent': 'Mozilla/5.0',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("HTTP Status Code:", resp.status)
        print("HTTP Headers:")
        for k, v in resp.headers.items():
            print(f"  {k}: {v}")
        
        body = resp.read().decode('utf-8', errors='ignore')
        print(f"\nHTTP Body Length: {len(body)}")
        # Check first 500 chars of HTTP body to see title or markers
        print("First 300 chars of body:")
        print(repr(body[:300]))
except Exception as e:
    print("HTTP Error:", e)
