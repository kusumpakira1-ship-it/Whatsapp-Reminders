import ftplib
import sys

sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

items = []
ftp.retrlines('LIST /', items.append)
print("=== ROOT DIR (/) ===")
for i in items:
    print(i)

items_sub = []
ftp.retrlines('LIST /public_html', items_sub.append)
print("\n=== PUBLIC_HTML DIR (/public_html) ===")
for i in items_sub:
    print(i)

ftp.quit()
