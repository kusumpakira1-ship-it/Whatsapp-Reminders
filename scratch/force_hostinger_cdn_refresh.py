import ftplib
import io
import sys
import urllib.request
import time

sys.stdout.reconfigure(encoding='utf-8')

print("=== 1. PREPARING INDEX.PHP WITH FRESH TIMESTAMP HEADER ===")
local_index_path = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\index.php'
with open(local_index_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Prepend dynamic timestamp comment and headers at the very top of index.php
timestamp_tag = f"<?php // Live Update Timestamp: {time.time()} ?>\n"
if not content.startswith("<?php // Live Update Timestamp:"):
    content = timestamp_tag + content

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

paths = [
    '/public_html/index.php',
    '/public_html/kusum/index.php',
    '/public_html/kusum/Whatsapp_Rem/index.php',
    '/public_html/kusum/Whatsapp_Rem/index1.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/index.php'
]

print("=== 2. UPLOADING FRESH TIMESTAMPED INDEX.PHP TO FTP ===")
for p in paths:
    try:
        ftp.storbinary(f'STOR {p}', io.BytesIO(content.encode('utf-8')))
        print(f"[OK] Uploaded -> {p}")
    except Exception as e:
        print(f"[ERR] Failed {p}: {e}")

ftp.quit()

print("\n=== 3. CALLING CLEAR CACHE OVER HTTP ===")
try:
    req_clear = urllib.request.Request("https://sunfragroup.com/kusum/Whatsapp_Rem/purge_all.php?t=" + str(time.time()), headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_clear, timeout=10) as r:
        print("Purge all response:", r.read().decode('utf-8', errors='ignore'))
except Exception as e:
    print("Purge error:", e)

time.sleep(2)

print("\n=== 4. TESTING LIVE HTTP RESPONSE FROM WEBSITE ===")
url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?cache_flush={time.time()}"
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
            print("\n🎉 SUCCESS! LIVE WEBSITE NOW SERVES MON TO SAT AND MON TO FRI!")
except Exception as e:
    print(f"Fetch error: {e}")
