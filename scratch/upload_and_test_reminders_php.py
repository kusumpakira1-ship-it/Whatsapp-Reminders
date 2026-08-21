"""
Upload full frontend code to reminders.php on FTP and test HTTP access.
"""
import ftplib, io, sys, urllib.request, time
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
        ftp.storbinary('STOR reminders.php', io.BytesIO(code))
        print(f"Uploaded reminders.php to {p} ✅")
    except Exception as e:
        print(f"Failed {p}: {e}")

ftp.quit()

time.sleep(2)

# Test live HTTP access to reminders.php
urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/reminders.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/reminders.php'
]

for url in urls:
    full_url = f"{url}?t={int(time.time())}"
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"\nURL: {full_url}")
            print(f"  Status: {resp.status}, Size: {len(html)} bytes")
            print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
            print(f"  Has 'changeRemindersViewingDate': {'changeRemindersViewingDate' in html}")
            print(f"  Has 'confirmToggleSubReport': {'confirmToggleSubReport' in html}")
    except Exception as e:
        print(f"Error {full_url}: {e}")

