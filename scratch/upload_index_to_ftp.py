"""
Upload frontend/index.php to Hostinger FTP server using storbinary.
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

target_remote_path = '/public_html/kusum/Whatsapp_Rem/frontend/index.php'
local_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'

print(f"Uploading {local_file} -> {target_remote_path} via storbinary...")
with open(local_file, 'rb') as f:
    ftp.storbinary(f'STOR {target_remote_path}', f)

print("✅ Upload successful!")
ftp.quit()

