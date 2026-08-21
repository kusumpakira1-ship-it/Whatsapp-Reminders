"""
Debug exact file being served by Apache for https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php
"""

import ftplib, urllib.request, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

debug_php = b"<?php echo 'EXACT_HOSTINGER_FILE_PATH: ' . __FILE__; exit; ?>"

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

dirs = [
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/frontend',
    '/public_html'
]

for d in dirs:
    try:
        ftp.cwd(d)
        ftp.storbinary('STOR debug_file_location.php', io.BytesIO(debug_php))
        print(f"Uploaded debug_file_location.php to {d}")
    except Exception as e:
        print(f"Error {d}: {e}")

ftp.quit()

urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/debug_file_location.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/debug_file_location.php',
    'https://sunfragroup.com/frontend/debug_file_location.php',
    'https://sunfragroup.com/debug_file_location.php'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"URL: {u} => Output: {resp.read().decode('utf-8')}")
    except Exception as e:
        print(f"URL: {u} => Error: {e}")
