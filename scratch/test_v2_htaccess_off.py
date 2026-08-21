"""
Add .htaccess with RewriteEngine Off to /v2 and test /v2/index.php HTTP output!
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

htaccess_v2 = b"RewriteEngine Off\n"

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ftp.cwd('/public_html/kusum/Whatsapp_Rem/v2')
ftp.storbinary('STOR .htaccess', io.BytesIO(htaccess_v2))
print("Uploaded RewriteEngine Off .htaccess to /v2 ✅")

ftp.quit()

time.sleep(1)

test_url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/v2/index.php?t={int(time.time())}"
try:
    req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"\nLive HTTP Test /v2/index.php with RewriteEngine Off:")
        print(f"  Status: {resp.status}, Size: {len(html)} bytes")
        print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
        print(f"  Has 'changeRemindersViewingDate': {'changeRemindersViewingDate' in html}")
        print(f"  Has 'sub_reports_status': {'sub_reports_status' in html}")
except Exception as e:
    print("Error:", e)

