"""
The FTP files are correct (239K with new functions).
The HTTP response is serving an OLD cached version (197K) from CDN/OPcache.

Strategy: 
1. Upload a PHP file that when executed directly invalidates OPcache for index.php
2. Also try moving/renaming index.php to force cache miss
3. Try clearing .user.ini opcache settings
"""
import ftplib, urllib.request, sys, io, time
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Update .user.ini to completely disable opcache
user_ini = b"opcache.enable=0\ropcache.revalidate_freq=0\ropcache.validate_timestamps=1\rmax_file_uploads=20\r"
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.storbinary('STOR .user.ini', io.BytesIO(user_ini))
print("Updated /public_html/kusum/Whatsapp_Rem/frontend/.user.ini (opcache.enable=0)")

ftp.cwd('/public_html/kusum/Whatsapp_Rem')
ftp.storbinary('STOR .user.ini', io.BytesIO(user_ini))
print("Updated /public_html/kusum/Whatsapp_Rem/.user.ini (opcache.enable=0)")

# Upload comprehensive cache-busting PHP file
cache_clear_php = b"""<?php
// Comprehensive cache clearing
$cleared = [];

// 1. Invalidate OPcache for all files
if (function_exists('opcache_reset')) {
    opcache_reset();
    $cleared[] = 'opcache_reset';
}

if (function_exists('opcache_invalidate')) {
    $dirs = [__DIR__, dirname(__DIR__)];
    foreach ($dirs as $dir) {
        if (is_dir($dir)) {
            foreach (glob($dir . '/*.php') as $f) {
                opcache_invalidate($f, true);
                $cleared[] = 'invalidated:' . basename($f);
            }
        }
    }
}

// 2. clearstatcache
clearstatcache(true);
$cleared[] = 'clearstatcache';

// 3. Touch index.php to update its mtime
$idx = __DIR__ . '/index.php';
if (file_exists($idx)) {
    touch($idx);
    $cleared[] = 'touched_index_mtime_' . filemtime($idx);
}

// 4. Force CDN purge headers
header('X-LiteSpeed-Purge: *');
header('Surrogate-Control: no-store');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Content-Type: text/plain');

echo "CACHE_CLEARED\\n";
echo implode("\\n", $cleared);
echo "\\nDONE_AT: " . date('Y-m-d H:i:s');
?>"""

for d in ['/public_html/kusum/Whatsapp_Rem/frontend', '/public_html/kusum/Whatsapp_Rem']:
    ftp.cwd(d)
    ftp.storbinary('STOR clear_all_cache.php', io.BytesIO(cache_clear_php))
    print(f"Uploaded clear_all_cache.php to {d}")

ftp.quit()

time.sleep(1)

# Execute cache clearing on both paths
for url in [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/clear_all_cache.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/clear_all_cache.php',
]:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = resp.read().decode('utf-8', errors='ignore')
            print(f"\n{url}:")
            print(result[:500])
    except Exception as e:
        print(f"{url}: {e}")

time.sleep(2)
# Now test if index.php is updated
url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?t={int(time.time())}'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print(f"\nAfter cache clear, index.php:")
    print(f"  Size: {len(html)}")
    print(f"  Has 'confirmToggleSubReport': {'YES ✅' if 'confirmToggleSubReport' in html else 'NO ❌'}")
