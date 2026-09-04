import ftplib
import io
import sys
import urllib.request
import time

sys.stdout.reconfigure(encoding='utf-8')

print("=== 1. FETCHING CURRENT HTTP RESPONSE FROM LIVE WEBSITE ===")
url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache, no-store, must-revalidate', 'Pragma': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        http_html = resp.read().decode('utf-8', errors='ignore')
        print(f"Current HTTP Length: {len(http_html)} bytes")
        print(f"HTTP has 'Mon to Sat': {'Mon to Sat' in http_html or 'mon-sat' in http_html}")
except Exception as e:
    print(f"HTTP Error: {e}")
    http_html = ""

print("\n=== 2. CONNECTING TO FTP AND SEARCHING FOR ALL INDEX.PHP FILES ===")
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_index_paths = []

def scan_dir(path):
    try:
        items = []
        ftp.retrlines(f'LIST {path}', items.append)
        for item in items:
            parts = item.split()
            name = parts[-1]
            if name in ('.', '..'):
                continue
            full_path = f"{path.rstrip('/')}/{name}"
            is_dir = item.startswith('d')
            if is_dir:
                if full_path in ('/logs', '/.well-known', '/cgi-bin'):
                    continue
                scan_dir(full_path)
            else:
                if name.lower().endswith('.php') and ('index' in name.lower() or 'reminders' in name.lower() or 'app' in name.lower()):
                    all_index_paths.append(full_path)
    except Exception as e:
        pass

print("Scanning FTP directory tree...")
scan_dir('/public_html')
print(f"Found {len(all_index_paths)} PHP index/app files on FTP:")
for p in all_index_paths:
    print(" -", p)

print("\n=== 3. UPLOADING UPDATED INDEX.PHP TO ALL FOUND LOCATIONS ===")
local_index = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\index.php'
with open(local_index, 'rb') as f:
    local_content = f.read()

for p in all_index_paths:
    try:
        ftp.storbinary(f'STOR {p}', io.BytesIO(local_content))
        print(f"Updated: {p}")
    except Exception as e:
        print(f"Failed to update {p}: {e}")

# Upload force_reset PHP script
reset_php = """<?php
@ini_set('opcache.revalidate_freq', '0');
@ini_set('opcache.enable', '0');
if (function_exists('opcache_reset')) { opcache_reset(); }
@header("X-LiteSpeed-Purge: *");
echo "OPCACHE_RESET_OK";
""".encode('utf-8')

reset_target = '/public_html/kusum/Whatsapp_Rem/clear_cache.php'
try:
    ftp.storbinary(f'STOR {reset_target}', io.BytesIO(reset_php))
    print(f"Uploaded cache reset script to {reset_target}")
except Exception as e:
    print(f"Failed reset script upload: {e}")

ftp.quit()

print("\n=== 4. TRIGGERING CACHE PURGE & VERIFYING LIVE HTTP RESPONSE ===")
try:
    urllib.request.urlopen("https://sunfragroup.com/kusum/Whatsapp_Rem/clear_cache.php", timeout=10)
    print("Triggered clear_cache.php endpoint.")
except Exception as e:
    print(f"Clear cache error: {e}")

time.sleep(2)

# Query live website with cache-busting query parameter
bypass_url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?v={int(time.time())}"
req2 = urllib.request.Request(bypass_url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache, no-store, must-revalidate'})
try:
    with urllib.request.urlopen(req2, timeout=15) as resp:
        fresh_html = resp.read().decode('utf-8', errors='ignore')
        print(f"Fresh HTTP Length: {len(fresh_html)} bytes")
        has_mon_sat = 'value="mon-sat"' in fresh_html or 'Mon to Sat' in fresh_html
        has_mon_fri = 'value="mon-fri"' in fresh_html or 'Mon to Fri' in fresh_html
        print(f"Contains 'Mon to Sat': {has_mon_sat}")
        print(f"Contains 'Mon to Fri': {has_mon_fri}")
        if has_mon_sat and has_mon_fri:
            print("LIVE WEBSITE VERIFICATION PASSED SUCCESSFULLY!")
        else:
            print("Still cached or different URL structure.")
except Exception as e:
    print(f"Fetch error: {e}")
