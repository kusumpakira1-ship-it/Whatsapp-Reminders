"""
Check all files in /public_html/kusum/Whatsapp_Rem and /public_html/kusum/Whatsapp_Rem/frontend
"""
import ftplib, io, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("=== Files in /public_html/kusum/Whatsapp_Rem ===")
ftp.cwd('/public_html/kusum/Whatsapp_Rem')
entries = []
ftp.retrlines('LIST', entries.append)
for e in entries:
    print(e)

print("\n=== Files in /public_html/kusum/Whatsapp_Rem/frontend ===")
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
entries = []
ftp.retrlines('LIST', entries.append)
for e in entries:
    print(e)

ftp.quit()

