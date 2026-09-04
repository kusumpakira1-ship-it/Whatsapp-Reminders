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

view_paths = [
    '/public_html/view.php',
    '/public_html/kusum/view.php',
    '/public_html/kusum/Whatsapp_Rem/view.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/view.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/reminders.php',
    '/public_html/kusum/Whatsapp_Rem/reminders.php',
    '/public_html/kusum/Whatsapp_Rem/dashboard.php',
    '/public_html/kusum/Whatsapp_Rem/dashboard2.php',
    '/public_html/kusum/Whatsapp_Rem/app.php'
]

print("=== OVERWRITING ALL VIEW.PHP & DASHBOARD.PHP LOCATIONS ON FTP ===")
for vp in view_paths:
    try:
        ftp.storbinary(f'STOR {vp}', io.BytesIO(local_content))
        print(f"[OK] Updated -> {vp}")
    except Exception as e:
        print(f"[ERR] Failed {vp}: {e}")

ftp.quit()

print("\n=== VERIFYING LIVE HTTP RESPONSE FROM WEBSITE ===")
time.sleep(2)
url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?v={time.time()}"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
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
            print("\n🎉 SUCCESS! LIVE WEBSITE NOW REFLECTS MON TO SAT AND MON TO FRI!")
        else:
            print("\nStill not showing, checking response length...")
except Exception as e:
    print(f"Fetch error: {e}")
