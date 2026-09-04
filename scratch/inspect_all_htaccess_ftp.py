import ftplib
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_htaccess = []

def scan_ht(path):
    try:
        items = []
        ftp.retrlines(f'LIST -a {path}', items.append)
        for item in items:
            parts = item.split()
            name = parts[-1]
            if name in ('.', '..'): continue
            full = f"{path.rstrip('/')}/{name}"
            if item.startswith('d'):
                if full not in ('/logs', '/.well-known', '/cgi-bin'):
                    scan_ht(full)
            else:
                if name.lower() == '.htaccess' or name.lower() == '.user.ini':
                    all_htaccess.append(full)
    except Exception as e:
        pass

scan_ht('/')
scan_ht('/public_html')

print(f"Found {len(all_htaccess)} configuration files:")
for ht in set(all_htaccess):
    print(f"\n==================== {ht} ====================")
    try:
        buf = io.BytesIO()
        ftp.retrbinary(f'RETR {ht}', buf.write)
        print(buf.getvalue().decode('utf-8', errors='ignore'))
    except Exception as e:
        print(f"Error reading {ht}: {e}")

ftp.quit()
