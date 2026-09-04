import ftplib
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

all_files = []

def scan_all(path):
    try:
        items = []
        ftp.retrlines(f'LIST {path}', items.append)
        for item in items:
            parts = item.split()
            name = parts[-1]
            if name in ('.', '..'): continue
            full = f"{path.rstrip('/')}/{name}"
            if item.startswith('d'):
                if full not in ('/logs', '/.well-known', '/cgi-bin'):
                    scan_all(full)
            else:
                all_files.append(full)
    except Exception as e:
        pass

scan_all('/public_html')

print(f"Scanning {len(all_files)} total files on Hostinger...")
for fp in all_files:
    if not fp.endswith(('.php', '.html', '.htm')): continue
    try:
        buf = io.BytesIO()
        ftp.retrbinary(f'RETR {fp}', buf.write)
        content = buf.getvalue().decode('utf-8', errors='ignore')
        if '<title>Reminders</title>' in content or 'Schedule Frequency' in content:
            has_mon_sat = 'mon-sat' in content or 'Mon to Sat' in content
            print(f"MATCH: {fp} (len={len(content)}, has_mon_sat={has_mon_sat})")
    except Exception as e:
        pass

ftp.quit()
