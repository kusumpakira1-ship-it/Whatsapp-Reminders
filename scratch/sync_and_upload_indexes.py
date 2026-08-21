"""
Copy frontend/index.php to root index.php and upload both to Hostinger FTP.
"""
import ftplib, io, sys, os
sys.stdout.reconfigure(encoding='utf-8')

frontend_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
root_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'

with open(frontend_file, 'rb') as f:
    code = f.read()

# Overwrite root index.php
with open(root_file, 'wb') as f:
    f.write(code)

print(f"Updated root index.php ({len(code)} bytes)")

# Upload to Hostinger FTP
try:
    ftp = ftplib.FTP()
    ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
    ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
    ftp.set_pasv(True)

    paths = [
        '/public_html/kusum/Whatsapp_Rem/frontend',
        '/public_html/kusum/Whatsapp_Rem',
        '/kusum/Whatsapp_Rem/frontend',
        '/kusum/Whatsapp_Rem',
        '/public_html/frontend',
        '/frontend'
    ]

    for p in paths:
        try:
            ftp.cwd(p)
            ftp.storbinary('STOR index.php', io.BytesIO(code))
            print(f"Uploaded to FTP path: {p}/index.php ✅")
        except Exception as e:
            print(f"Failed path {p}: {e}")

    ftp.quit()
    print("All FTP uploads completed successfully!")
except Exception as e:
    print("FTP Error:", e)

