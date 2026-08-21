"""
Upload new file app.php to FTP locations and test if it bypasses LiteSpeed cache!
"""
import ftplib, io, sys, urllib.request, time, json
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    code = f.read()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

paths = [
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/kusum/Whatsapp_Rem',
    '/kusum/Whatsapp_Rem/frontend',
    '/kusum/Whatsapp_Rem'
]

for p in paths:
    try:
        ftp.cwd(p)
        ftp.storbinary('STOR app.php', io.BytesIO(code))
        print(f"Uploaded app.php to {p}/app.php ✅")
    except Exception as e:
        print(f"Failed {p}: {e}")

ftp.quit()

time.sleep(2)

# Now test HTTP request to app.php
url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/app.php?t={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"\nHTTP Test app.php:")
        print(f"  Size: {len(html)} bytes")
        print(f"  Has 'confirmToggleSubReport': {'confirmToggleSubReport' in html}")
        print(f"  Has 'sub_reports_status': {'sub_reports_status' in html}")
except Exception as e:
    print(f"Error accessing app.php: {e}")

