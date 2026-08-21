"""
Upload view.php to /public_html/kusum/Whatsapp_Rem/frontend/view.php and test HTTP response!
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    code = f.read()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR view.php', io.BytesIO(code))
print("Uploaded view.php to /public_html/kusum/Whatsapp_Rem/frontend/view.php ✅")

ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR view.php', io.BytesIO(code))
print("Uploaded view.php to /public_html/kusum/Whatsapp_Rem/view.php ✅")

ftp.quit()

time.sleep(1)

urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/view.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/view.php'
]

for url in urls:
    full_url = f"{url}?t={int(time.time())}"
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"\nURL: {full_url}")
            print(f"  Status: {resp.status}, Size: {len(html)} bytes")
            print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
            print(f"  Has 'changeRemindersViewingDate': {'changeRemindersViewingDate' in html}")
            print(f"  Has 'sub_reports_status': {'sub_reports_status' in html}")
    except Exception as e:
        print(f"Error {full_url}: {e}")

