import ftplib
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

ftp_host = 'ftp.sunfragroup.com'
ftp_user = 'u632391467.kusum1'
ftp_pass = 'h3>R~fQ*z?m'

local_index = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\index.php'
local_app_index = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\app\static\index.php'
local_trigger = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\trigger_reminder.php'

print("=== CONNECTING TO HOSTINGER FTP ===")
try:
    ftp = ftplib.FTP()
    ftp.connect(ftp_host, 21, timeout=30)
    ftp.login(ftp_user, ftp_pass)
    ftp.set_pasv(True)
    print("Connected to FTP successfully!")

    target_files = [
        ('/public_html/kusum/Whatsapp_Rem/index.php', local_index),
        ('/public_html/kusum/Whatsapp_Rem/index1.php', local_index),
        ('/public_html/kusum/Whatsapp_Rem/frontend/index.php', local_app_index),
        ('/public_html/kusum/Whatsapp_Rem/trigger_reminder.php', local_trigger),
        ('/public_html/index.php', local_index),
    ]

    for remote_path, local_path in target_files:
        try:
            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)
            print(f"[OK] Uploaded -> {remote_path}")
        except Exception as fe:
            print(f"[ERR] Upload failed {remote_path}: {fe}")

    ftp.quit()
    print("FTP Upload Finished!")

except Exception as e:
    print(f"FTP Error: {e}")

print("\n=== VERIFYING LIVE WEBSITE HTML ===")
url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?v=" + str(int(urllib.parse.quote('123')))
req = urllib.request.Request("https://sunfragroup.com/kusum/Whatsapp_Rem/index.php", headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Fetched HTML Length: {len(html)} bytes")
        has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
        has_mon_fri = 'value="mon-fri"' in html or 'Mon to Fri' in html
        print(f"Contains 'Mon to Sat': {has_mon_sat}")
        print(f"Contains 'Mon to Fri': {has_mon_fri}")
        if has_mon_sat and has_mon_fri:
            print("LIVE WEBSITE VERIFICATION PASSED SUCCESSFULLY!")
        else:
            print("WARNING: HTML did not match expected tags yet. Checking cache.")
except Exception as e:
    print(f"HTTP fetch error: {e}")
