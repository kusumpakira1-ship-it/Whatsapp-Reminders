"""
Upload unique where_am_i.php to all directories and test which directory is actually served by HTTP!
"""
import ftplib, io, sys, urllib.request, time
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_dirs = [
    '/',
    '/public_html',
    '/public_html/frontend',
    '/public_html/kusum',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/public',
    '/public_html/Whatsapp_Rem',
    '/kusum',
    '/kusum/Whatsapp_Rem',
    '/kusum/Whatsapp_Rem/frontend'
]

for d in all_dirs:
    try:
        ftp.cwd(d)
        content = f"<?php echo json_encode(['path' => '{d}', 'file' => __FILE__, 'time' => time()]); ?>".encode('utf-8')
        ftp.storbinary('STOR where_am_i.php', io.BytesIO(content))
        print(f"Uploaded where_am_i.php to {d} ✅")
    except Exception as e:
        print(f"Failed {d}: {e}")

ftp.quit()

time.sleep(1)

test_urls = [
    'https://sunfragroup.com/where_am_i.php',
    'https://sunfragroup.com/frontend/where_am_i.php',
    'https://sunfragroup.com/kusum/where_am_i.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/where_am_i.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/where_am_i.php',
    'https://sunfragroup.com/Whatsapp_Rem/where_am_i.php',
    'https://sunfragroup.com/public/where_am_i.php'
]

print("\n--- Testing HTTP URLs ---")
for url in test_urls:
    full_url = f"{url}?t={int(time.time())}"
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8')
            print(f"URL: {full_url}")
            print(f"  Response: {content}\n")
    except Exception as e:
        print(f"Error {full_url}: {e}\n")

