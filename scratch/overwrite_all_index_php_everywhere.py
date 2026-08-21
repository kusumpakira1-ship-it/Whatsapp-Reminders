"""
Overwrite ALL index.php files across ALL Hostinger directories with the exact new code.
"""
import ftplib, io, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    code = f.read()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_paths = [
    '/public_html',
    '/public_html/frontend',
    '/public_html/kusum',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/public',
    '/public_html/Whatsapp_Rem',
    '/kusum',
    '/kusum/Whatsapp_Rem',
    '/kusum/Whatsapp_Rem/frontend'
]

for p in all_paths:
    try:
        ftp.cwd(p)
        ftp.storbinary('STOR index.php', io.BytesIO(code))
        print(f"Uploaded to {p}/index.php ({len(code)} bytes) ✅")
    except Exception as e:
        print(f"Failed {p}: {e}")

ftp.quit()
print("All index.php files updated across every directory!")

