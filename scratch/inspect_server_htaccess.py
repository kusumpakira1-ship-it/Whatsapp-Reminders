"""
Read .htaccess and index.php from Hostinger FTP to inspect URL rewrite and caching
"""

import ftplib, io, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')

ht_buf = io.BytesIO()
try:
    ftp.retrbinary('RETR .htaccess', ht_buf.write)
    print("=== .htaccess content in frontend/ ===")
    print(ht_buf.getvalue().decode('utf-8'))
except Exception as e:
    print(".htaccess read error:", e)

# Read index.php from FTP
idx_buf = io.BytesIO()
ftp.retrbinary('RETR index.php', idx_buf.write)
code = idx_buf.getvalue().decode('utf-8', errors='ignore')

print("\n=== index.php on FTP info ===")
print("• Size:", len(code), "bytes")
print("• Has confirmToggleSubReport on FTP file?", "confirmToggleSubReport" in code)

ftp.quit()
