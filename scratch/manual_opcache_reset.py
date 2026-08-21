"""
Strategy:
1. Remove frontend/.htaccess so PHP files execute directly (not redirected to old index.php)
2. Upload + execute opcache_reset() script
3. Restore .htaccess
4. Verify new content is live
"""
import ftplib, io, urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    new_code = f.read()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

frontend_dir = '/public_html/kusum/Whatsapp_Rem/frontend'
root_dir = '/public_html/kusum/Whatsapp_Rem'

# Step 1: Remove frontend .htaccess so files execute directly
ftp.cwd(frontend_dir)
try:
    ftp.rename('.htaccess', '.htaccess_disabled')
    print("Step 1: Disabled frontend/.htaccess ✅")
except Exception as e:
    print(f"Step 1: {e}")

# Step 2: Upload opcache reset script
reset_php = b"""<?php
header('Content-Type: text/plain');
header('Cache-Control: no-store, no-cache');
$results = [];

// Reset OPcache
if (function_exists('opcache_reset')) {
    $r = opcache_reset();
    $results[] = 'opcache_reset: ' . ($r ? 'SUCCESS' : 'FAILED');
} else {
    $results[] = 'opcache_reset: NOT AVAILABLE';
}

// Invalidate specific files
$files = [
    __DIR__ . '/index.php',
    dirname(__DIR__) . '/index.php',
];
foreach ($files as $f) {
    if (file_exists($f) && function_exists('opcache_invalidate')) {
        $r = opcache_invalidate($f, true);
        $results[] = 'invalidate ' . basename(dirname($f)) . '/index.php: ' . ($r ? 'OK' : 'FAIL');
    }
}

clearstatcache(true);
$results[] = 'clearstatcache: OK';
$results[] = 'EXECUTED_FROM: ' . __FILE__;
$results[] = 'TIME: ' . date('Y-m-d H:i:s');

// OPcache status
if (function_exists('opcache_get_status')) {
    $status = opcache_get_status(false);
    $results[] = 'opcache.enable: ' . ($status ? 'ON' : 'OFF');
    if ($status) {
        $results[] = 'cached_scripts: ' . ($status['opcache_statistics']['num_cached_scripts'] ?? 'unknown');
    }
}

echo implode("\n", $results);
?>"""

ftp.storbinary('STOR do_reset.php', io.BytesIO(reset_php))
print("Step 2: Uploaded do_reset.php ✅")

ftp.quit()

# Step 3: Execute the reset script
time.sleep(1)
print("\nStep 3: Executing opcache reset...")
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/do_reset.php?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = resp.read().decode('utf-8', errors='ignore')
        print(f"Reset result:\n{result}")
        success = 'SUCCESS' in result or 'EXECUTED_FROM' in result
except Exception as e:
    result = str(e)
    success = False
    print(f"Error: {e}")

# Step 4: Restore .htaccess
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)
ftp.cwd(frontend_dir)

htaccess = b"""RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php [L]

<IfModule mod_headers.c>
    Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0"
    Header set Pragma "no-cache"
    Header set Expires "0"
</IfModule>
"""
try:
    ftp.rename('.htaccess_disabled', '.htaccess')
    print("\nStep 4: Restored .htaccess ✅")
except:
    ftp.storbinary('STOR .htaccess', io.BytesIO(htaccess))
    print("\nStep 4: Uploaded fresh .htaccess ✅")

ftp.quit()

# Step 5: Verify
time.sleep(2)
print("\nStep 5: Verifying live site...")
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?v={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    has_toggle = 'confirmToggleSubReport' in html
    print(f"  Size: {len(html)}")
    print(f"  Has 'confirmToggleSubReport': {'YES ✅ LIVE!' if has_toggle else 'NO ❌ Still cached'}")
