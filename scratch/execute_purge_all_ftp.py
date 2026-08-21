"""
Create purge_all.php on Hostinger FTP to flush OPcache, LiteSpeed cache, and APCu.
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

purge_script = b"""<?php
header("Cache-Control: no-cache, no-store, must-revalidate, max-age=0");
header("Pragma: no-cache");
header("Expires: 0");
header("X-LiteSpeed-Purge: *");

$res = [];
if (function_exists('opcache_reset')) {
    $res['opcache_reset'] = opcache_reset();
}
if (function_exists('apcu_clear_cache')) {
    $res['apcu_clear_cache'] = apcu_clear_cache();
}

// Clear any stat cache
clearstatcache(true);

echo json_encode(['status' => 'success', 'purged' => true, 'details' => $res, 'time' => date('Y-m-d H:i:s')]);
"""

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
        ftp.storbinary('STOR purge_all.php', io.BytesIO(purge_script))
        print(f"Uploaded purge_all.php to {p} ✅")
    except Exception as e:
        print(f"Failed {p}: {e}")

ftp.quit()

time.sleep(1)

# Execute purge_all.php via HTTP
for p in ['/kusum/Whatsapp_Rem/frontend/purge_all.php', '/kusum/Whatsapp_Rem/purge_all.php']:
    url = f"https://sunfragroup.com{p}?t={int(time.time())}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"Executed {url} -> {resp.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error {url}: {e}")

