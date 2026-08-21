"""
Find EVERY index.php and index.html file across the ENTIRE FTP root directory tree!
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

found_files = []

def scan_dir(dir_path):
    try:
        ftp.cwd(dir_path)
        items = []
        ftp.retrlines('LIST', items.append)
        for item in items:
            parts = item.split()
            if not parts: continue
            name = parts[-1]
            size = parts[4] if len(parts) > 4 else '0'
            is_dir = item.startswith('d')
            full_path = (dir_path.rstrip('/') + '/' + name).replace('//', '/')
            if is_dir:
                if name not in ['.', '..', '.git', '.well-known']:
                    scan_dir(full_path)
            else:
                if name in ['index.php', 'index.html', 'app.php', 'main.php']:
                    found_files.append((full_path, size))
    except Exception as e:
        pass

scan_dir('/')
ftp.quit()

print("=== ALL INDEX/APP/MAIN FILES ON FTP SERVER ===")
for path, size in found_files:
    print(f"Path: {path} | Size: {size} bytes")

