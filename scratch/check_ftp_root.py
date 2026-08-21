"""
Check FTP root directory and find the 197K file
"""
import ftplib, io, urllib.request, time
import sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("FTP root listing:")
ftp.cwd('/')
entries = []
ftp.retrlines('LIST', entries.append)
for e in entries[:20]:
    print(e)

# Also the FTP Simple temp file at root corresponds to what path?
# The temp file is: cedad.../index.php (no subdirectory under session root)
# This maps to the FTP connection root, which depends on how FTP Simple is configured
# Common: /public_html or /public_html/kusum/Whatsapp_Rem/frontend

# The user opened the file from Hostinger. Let me check kusum-level index.php
print("\n")
for path in [
    '/public_html/kusum/index.php',
    '/public_html/index.php',
]:
    try:
        ftp.cwd('/')
        buf = io.BytesIO()
        ftp.retrbinary(f'RETR {path}', buf.write)
        c = buf.getvalue().decode('utf-8', errors='ignore')
        has_toggle = 'confirmToggleSubReport' in c
        print(f"{path}: {len(c)} bytes, has_toggle={has_toggle}")
    except Exception as e:
        print(f"{path}: {e}")

ftp.quit()
