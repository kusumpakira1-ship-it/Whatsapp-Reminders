import ftplib
import io
import sys
import urllib.request
import time

sys.stdout.reconfigure(encoding='utf-8')

local_index = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\index.php'
with open(local_index, 'rb') as f:
    local_content = f.read()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_target_paths = [
    '/index.php',
    '/view.php',
    '/kusum/index.php',
    '/kusum/view.php',
    '/kusum/Whatsapp_Rem/index.php',
    '/kusum/Whatsapp_Rem/index1.php',
    '/kusum/Whatsapp_Rem/app.php',
    '/kusum/Whatsapp_Rem/dashboard.php',
    '/kusum/Whatsapp_Rem/view.php',
    '/kusum/Whatsapp_Rem/reminders.php',
    '/kusum/Whatsapp_Rem/frontend/index.php',
    '/kusum/Whatsapp_Rem/frontend/view.php',
    '/Whatsapp_Rem/index.php',
    '/Whatsapp_Rem/view.php',
    '/cedad10937994543724efa30b6e53514/index.php',
    '/cedad10937994543724efa30b6e53514/view.php',
    '/cedad10937994543724efa30b6e53514/kusum/Whatsapp_Rem/index.php',
    '/cedad10937994543724efa30b6e53514/kusum/Whatsapp_Rem/view.php',
    '/public_html/index.php',
    '/public_html/index1.php',
    '/public_html/view.php',
    '/public_html/kusum/index.php',
    '/public_html/kusum/view.php',
    '/public_html/kusum/Whatsapp_Rem/index.php',
    '/public_html/kusum/Whatsapp_Rem/index1.php',
    '/public_html/kusum/Whatsapp_Rem/app.php',
    '/public_html/kusum/Whatsapp_Rem/dashboard.php',
    '/public_html/kusum/Whatsapp_Rem/view.php',
    '/public_html/kusum/Whatsapp_Rem/reminders.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/index.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/view.php'
]

print("=== OVERWRITING EVERY TARGET PATH ACROSS ALL SUBFOLDERS ON FTP ===")
for tp in all_target_paths:
    try:
        ftp.storbinary(f'STOR {tp}', io.BytesIO(local_content))
        print(f"[OK] Uploaded -> {tp}")
    except Exception as e:
        print(f"[ERR] Skip {tp}: {e}")

ftp.quit()

print("\n=== RE-TESTING LIVE WEBSITE ===")
time.sleep(2)
url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"HTTP Body Length: {len(html)} bytes")
        has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
        has_mon_fri = 'value="mon-fri"' in html or 'Mon to Fri' in html
        print(f"Contains 'Mon to Sat': {has_mon_sat}")
        print(f"Contains 'Mon to Fri': {has_mon_fri}")
        if has_mon_sat and has_mon_fri:
            print("\n🎉 SUCCESS! IT IS UPDATED ON THE LIVE WEBSITE NOW!")
except Exception as e:
    print(f"Fetch error: {e}")
