import ftplib
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
        ftp.retrlines(f'LIST -a {path}', items.append)
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
    except Exception:
        pass

scan_all('/public_html')

html_files = [f for f in all_files if f.lower().endswith(('.html', '.htm')) or 'index' in f.lower()]
print(f"Found {len(html_files)} html/index files:")
for hf in html_files:
    print(" -", hf)

ftp.quit()
