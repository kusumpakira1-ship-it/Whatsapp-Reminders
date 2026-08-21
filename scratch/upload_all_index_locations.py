"""
Check all index.php remote file locations on FTP and update them with local frontend/index.php.
"""
import ftplib, sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

local_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'

remote_locations = [
    '/public_html/kusum/Whatsapp_Rem/frontend/index.php',
    '/public_html/kusum/Whatsapp_Rem/index.php',
    '/public_html/frontend/index.php',
    '/public_html/index.php'
]

for remote in remote_locations:
    print(f"Uploading to {remote}...")
    try:
        with open(local_file, 'rb') as f:
            ftp.storbinary(f'STOR {remote}', f)
        print(f"  ✅ Uploaded {remote}")
    except Exception as e:
        print(f"  ❌ Error uploading {remote}: {e}")

ftp.quit()

print("\n--- RE-TESTING LIVE WEB SERVER HTML ---")
url = "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print("Fetched HTML Total Length:", len(html))
    print("Contains 'confirmToggleSubReport':", "confirmToggleSubReport" in html)
    print("Contains 'resetAllSubReports':", "resetAllSubReports" in html)
    print("Contains 'Undone':", "Undone" in html)

