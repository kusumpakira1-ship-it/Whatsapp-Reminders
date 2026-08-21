"""
Overwrite EVERY index.php file across ALL root folders (/Whatsapp_Rem, /cedad..., /public, /, /kusum, /public_html) with the exact updated code!
"""
import ftplib, io, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php', 'rb') as f:
    code = f.read()

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_paths_to_update = [
    '/',
    '/public',
    '/frontend',
    '/Whatsapp_Rem',
    '/Whatsapp_Rem/frontend',
    '/kusum',
    '/kusum/Whatsapp_Rem',
    '/kusum/Whatsapp_Rem/frontend',
    '/cedad10937994543724efa30b6e53514',
    '/cedad10937994543724efa30b6e53514/public',
    '/cedad10937994543724efa30b6e53514/Whatsapp_Rem',
    '/cedad10937994543724efa30b6e53514/Whatsapp_Rem/frontend',
    '/public_html',
    '/public_html/public',
    '/public_html/frontend',
    '/public_html/kusum',
    '/public_html/kusum/index.php',
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html/Whatsapp_Rem',
    '/public_html/Whatsapp_Rem/frontend'
]

for p in all_paths_to_update:
    try:
        ftp.cwd(p)
        ftp.storbinary('STOR index.php', io.BytesIO(code))
        print(f"Successfully updated index.php at {p} ({len(code)} bytes) ✅")
    except Exception as e:
        print(f"Failed at {p}: {e}")

ftp.quit()
print("\n🎉 ALL SERVER INDEX.PHP FILES UPDATED ACROSS ALL ROOT DIRECTORIES!")

