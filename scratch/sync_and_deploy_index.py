"""
Copy frontend/index.php to root index.php and upload to Hostinger FTP
"""

import sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders')

# Copy frontend/index.php to root index.php
shutil.copyfile('frontend/index.php', 'index.php')
print("Copied frontend/index.php -> index.php cleanly!")

# Now upload to Hostinger FTP
import ftplib

ftp_host = "154.56.47.52"
ftp_user = "u923187232.kusum"
ftp_pass = "Kusum@123" # or loaded from config

try:
    ftp = ftplib.FTP(ftp_host)
    ftp.login(ftp_user, ftp_pass)
    print("FTP Connected successfully to Hostinger!")
    
    # Upload to frontend/index.php and index.php on Hostinger
    with open("frontend/index.php", "rb") as f:
        ftp.storbinary("STOR public_html/kusum/Whatsapp_Rem/frontend/index.php", f)
    print("Uploaded frontend/index.php to Hostinger FTP!")
    
    with open("index.php", "rb") as f:
        ftp.storbinary("STOR public_html/kusum/Whatsapp_Rem/index.php", f)
    print("Uploaded index.php to Hostinger FTP!")
    
    ftp.quit()
    print("FTP upload completed successfully!")
except Exception as e:
    print("FTP Upload note:", e)
