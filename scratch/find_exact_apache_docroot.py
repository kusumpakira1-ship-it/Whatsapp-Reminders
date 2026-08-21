"""
Find exact Apache DocumentRoot by writing test_func.php to all folders
"""

import ftplib, urllib.request, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

test_php = b"<?php echo 'TEST_FUNC_SUCCESS:' . __FILE__; ?>"

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

def upload_recursive(path):
    try:
        ftp.cwd(path)
        ftp.storbinary('STOR test_func.php', io.BytesIO(test_php))
        print(f"Uploaded test_func.php to {path}")
        items = ftp.nlst()
        for item in items:
            if item not in ['.', '..'] and '.' not in item:
                sub = path + '/' + item if path != '/' else '/' + item
                upload_recursive(sub)
    except Exception:
        pass

upload_recursive('/')
ftp.quit()

time.sleep(1)
urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/test_func.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/test_func.php',
    'https://sunfragroup.com/frontend/test_func.php',
    'https://sunfragroup.com/test_func.php'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        res = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
        print(f"URL: {u} => Output: {res}")
    except Exception as e:
        print(f"URL: {u} => Error: {e}")
