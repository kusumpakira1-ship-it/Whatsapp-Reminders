"""
Test where Apache is loading index.php from by fetching debug endpoint
"""
import sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

# Let's upload a small php file path_check_123.php to /public_html/kusum/Whatsapp_Rem/frontend/path_check_123.php
import ftplib
ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

code = b"<?php echo 'FILE: ' . __FILE__ . ' | SIZE: ' . filesize(__FILE__);"
import io
ftp.storbinary("STOR /public_html/kusum/Whatsapp_Rem/frontend/path_check_123.php", io.BytesIO(code))
ftp.storbinary("STOR /public_html/kusum/Whatsapp_Rem/path_check_123.php", io.BytesIO(code))
ftp.storbinary("STOR /public_html/kusum/path_check_123.php", io.BytesIO(code))
ftp.quit()

print("--- TESTING EXECUTED PHP PATHS ---")
urls = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/path_check_123.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/path_check_123.php",
    "https://sunfragroup.com/kusum/path_check_123.php"
]
for u in urls:
    try:
        r = requests.get(u + f"?v={time.time()}", timeout=10)
        print(f"URL {u} => {r.text}")
    except Exception as e:
        print(f"Error {u}: {e}")
