"""
Inspect .htaccess in all directories on FTP.
"""
import ftplib, io, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

paths = [
    '/',
    '/public_html',
    '/public_html/kusum',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
]

for p in paths:
    try:
        ftp.cwd(p)
        buf = io.BytesIO()
        ftp.retrbinary('RETR .htaccess', buf.write)
        print(f"\n--- .htaccess at {p} ---")
        print(buf.getvalue().decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"\n--- .htaccess at {p}: {e} ---")

ftp.quit()

