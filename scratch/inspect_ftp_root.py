"""
List directories under /public_html/ on Hostinger FTP.
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("=== LISTING /public_html/ ===")
files = []
ftp.cwd('/public_html/')
ftp.dir(files.append)
for f in files:
    print(f)

ftp.quit()

