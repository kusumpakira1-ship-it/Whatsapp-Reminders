"""
Add a unique timestamp comment to line 1 of frontend/index.php, upload via FTP, and call opcache_reset()!
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

frontend_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
root_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'

with open(frontend_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Prepend a fresh timestamp comment to force OPcache timestamp revalidation
ts_str = f"<?php // OPCACHE_FORCE_RECOMPILE_{int(time.time())}\n"
if content.startswith('<?php'):
    new_content = ts_str + content[5:]
else:
    new_content = ts_str + content

code = new_content.encode('utf-8')

with open(frontend_file, 'wb') as f:
    f.write(code)
with open(root_file, 'wb') as f:
    f.write(code)

print(f"Updated local index.php with timestamp comment ({len(code)} bytes)")

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

paths = [
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/kusum/Whatsapp_Rem',
    '/kusum/Whatsapp_Rem/frontend',
    '/kusum/Whatsapp_Rem',
    '/public_html/frontend',
    '/frontend'
]

for p in paths:
    try:
        ftp.cwd(p)
        ftp.storbinary('STOR index.php', io.BytesIO(code))
        print(f"Uploaded to FTP path: {p}/index.php ✅")
    except Exception as e:
        print(f"Failed path {p}: {e}")

ftp.quit()

time.sleep(1)

# Now call opcache_reset via HTTP script
reset_script = b"<?php opcache_reset(); clearstatcache(true); echo 'OPCACHE_FLUSHED'; ?>"
ftp2 = ftplib.FTP()
ftp2.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp2.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp2.set_pasv(True)

for p in ['/public_html/kusum/Whatsapp_Rem/frontend', '/public_html/kusum/Whatsapp_Rem']:
    try:
        ftp2.cwd(p)
        ftp2.storbinary('STOR flush_opcache.php', io.BytesIO(reset_script))
    except:
        pass
ftp2.quit()

time.sleep(1)

for url_path in ['/kusum/Whatsapp_Rem/frontend/flush_opcache.php', '/kusum/Whatsapp_Rem/flush_opcache.php']:
    try:
        req = urllib.request.Request(f"https://sunfragroup.com{url_path}?t={int(time.time())}")
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Executed {url_path}: {resp.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error {url_path}: {e}")

time.sleep(1)

# Check live index.php size!
test_url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?t={int(time.time())}"
try:
    req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"\nLive HTTP Test after OPcache Recompile:")
        print(f"  Size: {len(html)} bytes")
        print(f"  Has 'OPCACHE_FORCE_RECOMPILE': {'OPCACHE_FORCE_RECOMPILE' in html}")
        print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
        print(f"  Has 'sub_reports_status': {'sub_reports_status' in html}")
except Exception as e:
    print("Test Error:", e)

