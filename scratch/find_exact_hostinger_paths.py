"""
Find exact directory paths and upload updated files to Hostinger FTP
"""

import ftplib, sys, os
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("Current Directory:", ftp.pwd())
print("\nFiles in root:")
for item in ftp.nlst():
    print(" -", item)

# Let's check public_html
try:
    ftp.cwd('/public_html')
    print("\nFiles in /public_html:")
    for item in ftp.nlst():
        print(" -", item)
except Exception as e:
    print("public_html error:", e)

# Let's check kusum / Whatsapp_Rem
try:
    ftp.cwd('/public_html/kusum/Whatsapp_Rem')
    print("\nFiles in /public_html/kusum/Whatsapp_Rem:")
    for item in ftp.nlst():
        print(" -", item)
except Exception as e:
    print("kusum/Whatsapp_Rem error:", e)

try:
    ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
    print("\nFiles in /public_html/kusum/Whatsapp_Rem/frontend:")
    for item in ftp.nlst():
        print(" -", item)
except Exception as e:
    print("frontend error:", e)

ftp.quit()
