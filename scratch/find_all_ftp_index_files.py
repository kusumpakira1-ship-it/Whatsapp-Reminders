"""
Find all index.php files on Hostinger FTP server
"""

import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

def scan_dir(path):
    try:
        entries = []
        ftp.cwd(path)
        ftp.retrlines('LIST', entries.append)
        for e in entries:
            parts = e.split(maxsplit=8)
            if len(parts) < 9: continue
            name = parts[8]
            is_dir = e.startswith('d')
            full_path = f"{path}/{name}".replace('//', '/')
            if is_dir:
                if name not in ['.', '..', 'node_modules', '.git']:
                    scan_dir(full_path)
            elif name == 'index.php':
                size = parts[4]
                print(f"FOUND: {full_path} (size: {size} bytes)")
    except Exception as err:
        pass

scan_dir('/public_html')
ftp.quit()
