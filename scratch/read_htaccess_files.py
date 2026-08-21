"""
Read the .htaccess files on Hostinger FTP to understand redirect rules.
Also check what PHP file is ACTUALLY being served via HTTP by renaming index.php temporarily.
"""
import ftplib, sys, io
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

dirs_to_check = [
    '/public_html',
    '/public_html/kusum',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
]

for d in dirs_to_check:
    try:
        ftp.cwd(d)
        buf = io.BytesIO()
        ftp.retrbinary('RETR .htaccess', buf.write)
        content = buf.getvalue().decode('utf-8', errors='ignore')
        print(f"\n=== {d}/.htaccess ===")
        print(content)
    except Exception as e:
        print(f"\n{d}/.htaccess: {e}")

# Also list root files
print("\n=== /public_html/kusum/Whatsapp_Rem contents ===")
ftp.cwd('/public_html/kusum/Whatsapp_Rem')
entries = []
ftp.retrlines('LIST', entries.append)
for e in entries[:30]:
    print(e)

ftp.quit()
