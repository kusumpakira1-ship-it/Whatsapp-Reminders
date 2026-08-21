"""
Inject __FILE__ tracer into index.php on server to find the exact file being executed by Hostinger Apache
"""
import ftplib, sys, urllib.request, time, requests
sys.stdout.reconfigure(encoding='utf-8')

src_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
with open(src_file, 'r', encoding='utf-8') as f:
    code = f.read()

tracer_code = "<?php echo \"<!-- EXECUTED_FILE: \" . __FILE__ . \" | TIME: \" . date('Y-m-d H:i:s') . \" -->\\n\"; ?>\n" + code

import io
tracer_bytes = tracer_code.encode('utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("Uploading traced index.php to all locations...")
ftp.storbinary("STOR /public_html/kusum/Whatsapp_Rem/frontend/index.php", io.BytesIO(tracer_bytes))
ftp.storbinary("STOR /public_html/kusum/Whatsapp_Rem/index.php", io.BytesIO(tracer_bytes))
ftp.storbinary("STOR /public_html/kusum/index.php", io.BytesIO(tracer_bytes))
ftp.storbinary("STOR /public_html/frontend/index.php", io.BytesIO(tracer_bytes))
ftp.storbinary("STOR /public_html/index.php", io.BytesIO(tracer_bytes))
ftp.quit()

print("\nFetching live webpage over HTTP...")
url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?v={int(time.time())}"
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

for line in r.text.splitlines()[:15]:
    print(f"HEADER LINE: {line}")
