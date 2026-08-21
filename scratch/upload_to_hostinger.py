"""
Upload updated frontend/index.php and index.php to Hostinger FTP
"""

import ftplib, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders')

ftp = ftplib.FTP()
print("Connecting to ftp.sunfragroup.com...")
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)
print("Logged in successfully to Hostinger FTP!")

# 1. Upload to /public_html/kusum/Whatsapp_Rem/frontend/index.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
with open('frontend/index.php', 'rb') as f:
    ftp.storbinary('STOR index.php', f)
print("Uploaded frontend/index.php successfully!")

# 2. Upload to /public_html/kusum/Whatsapp_Rem/index.php
ftp.cwd('/public_html/kusum/Whatsapp_Rem')
with open('index.php', 'rb') as f:
    ftp.storbinary('STOR index.php', f)
print("Uploaded root index.php successfully!")

ftp.quit()
print("All files updated live on https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php !")
