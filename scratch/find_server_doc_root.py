"""
Create path_checker.php to return exact __FILE__, __DIR__, and document root!
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

checker_script = b"<?php echo json_encode(['file' => __FILE__, 'dir' => __DIR__, 'doc_root' => $_SERVER['DOCUMENT_ROOT'] ?? '', 'time' => time()]); ?>"

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

paths = [
    '/',
    '/public_html',
    '/public_html/kusum',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
]

for p in paths:
    try:
        ftp.cwd(p)
        ftp.storbinary('STOR path_checker.php', io.BytesIO(checker_script))
        print(f"Uploaded path_checker.php to {p} ✅")
    except Exception as e:
        print(f"Failed {p}: {e}")

ftp.quit()

time.sleep(1)

test_urls = [
    'https://sunfragroup.com/path_checker.php',
    'https://sunfragroup.com/kusum/path_checker.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/path_checker.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/path_checker.php',
]

for url in test_urls:
    full_url = f"{url}?t={int(time.time())}"
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8')
            print(f"URL: {full_url} -> {content}")
    except Exception as e:
        print(f"Error {full_url}: {e}")

