"""
Inspect files in /public_html/farm/sunfra/ on Hostinger FTP.
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("=== LISTING /public_html/farm/sunfra/ ===")
files = []
try:
    ftp.cwd('/public_html/farm/sunfra/')
    ftp.dir(files.append)
    for f in files[:30]:
        print(f)
except Exception as e:
    print("Error:", e)

ftp.quit()

