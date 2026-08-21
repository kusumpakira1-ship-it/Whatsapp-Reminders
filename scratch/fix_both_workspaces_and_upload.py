"""
Copy updated frontend/index.php to both workspace paths and upload to Hostinger FTP
"""

import ftplib, shutil, sys, time, io, os
sys.stdout.reconfigure(encoding='utf-8')

src_file = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'
dest_files = [
    r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\frontend\index.php',
    r'c:\Users\sunfra\Desktop\Whatsapp Reminders\index.php'
]

for d in dest_files:
    try:
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copyfile(src_file, d)
        print(f"Copied to {d} ✅")
    except Exception as e:
        print(f"Note copying to {d}: {e}")

with open(src_file, 'rb') as f:
    code = f.read()

print(f"File size: {len(code)} bytes")
print("Has confirmToggleSubReport in local file?", b"confirmToggleSubReport" in code)

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

target_ftp_dirs = [
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Reminders/frontend',
    '/public_html/kusum/Whatsapp_Reminders'
]

for d in target_ftp_dirs:
    try:
        ftp.cwd(d)
        ftp.storbinary('STOR index.php', io.BytesIO(code))
        print(f"Uploaded to FTP path: {d}/index.php ✅")
    except Exception as e:
        print(f"Note FTP path {d}: {e}")

ftp.quit()

print("\nAll workspace files and FTP locations updated!")
