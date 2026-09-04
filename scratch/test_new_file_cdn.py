import ftplib
import io
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

test_code = """<?php
echo "HELLO_LIVE_TEST_123_MON_SAT_MON_FRI";
""".encode('utf-8')

test_path = '/public_html/kusum/Whatsapp_Rem/test_new_page_123.php'
ftp.storbinary(f'STOR {test_path}', io.BytesIO(test_code))
ftp.quit()

print("Uploaded test_new_page_123.php")

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/test_new_page_123.php"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as res:
        out = res.read().decode('utf-8', errors='ignore')
        print(f"URL {url} => {out}")
except Exception as e:
    print(f"Error fetching {url}: {e}")
