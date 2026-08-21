"""
Upload force_reset_999.php to reset OPcache on Hostinger PHP-FPM
"""
import ftplib, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

reset_php_code = """<?php
@ini_set('opcache.revalidate_freq', '0');
@ini_set('opcache.enable', '0');

if (function_exists('opcache_reset')) {
    $res = opcache_reset();
    echo "opcache_reset(): " . ($res ? 'TRUE' : 'FALSE') . "\n";
} else {
    echo "opcache_reset() function not available\n";
}

$files = [
    __DIR__ . '/index.php',
    __DIR__ . '/../index.php',
    __DIR__ . '/../../index.php'
];

foreach ($files as $f) {
    if (file_exists($f)) {
        if (function_exists('opcache_invalidate')) {
            $inv = opcache_invalidate($f, true);
            echo "opcache_invalidate({$f}): " . ($inv ? 'TRUE' : 'FALSE') . "\n";
        }
        @touch($f, time());
        echo "Touched {$f}\n";
    }
}
echo "DONE OPCACHE RESET";
""".encode('utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

import io
print("Uploading force_reset_999.php to FTP...")
ftp.storbinary("STOR /public_html/kusum/Whatsapp_Rem/frontend/force_reset_999.php", io.BytesIO(reset_php_code))
ftp.storbinary("STOR /public_html/kusum/Whatsapp_Rem/force_reset_999.php", io.BytesIO(reset_php_code))
ftp.storbinary("STOR /public_html/kusum/force_reset_999.php", io.BytesIO(reset_php_code))
ftp.quit()

print("\nTriggering force_reset_999.php over HTTP...")
urls = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/force_reset_999.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/force_reset_999.php",
    "https://sunfragroup.com/kusum/force_reset_999.php"
]

for url in urls:
    try:
        req = urllib.request.Request(url + f"?v={time.time()}", headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req, timeout=10)
        out = res.read().decode('utf-8', errors='ignore')
        print(f"URL {url} => {out}")
    except Exception as e:
        print(f"URL {url} Error: {e}")

