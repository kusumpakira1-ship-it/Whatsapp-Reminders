"""
Find all index.php files in public_html and check their exact byte sizes on disk!
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

def find_files(dir_path):
    try:
        ftp.cwd(dir_path)
        items = []
        ftp.retrlines('LIST', items.append)
        for item in items:
            parts = item.split()
            name = parts[-1]
            size = parts[4]
            is_dir = item.startswith('d')
            full_path = f"{dir_path}/{name}".replace('//', '/')
            if is_dir and name not in ['.', '..']:
                find_files(full_path)
            elif name == 'index.php':
                print(f"FILE: {full_path} -> Size: {size} bytes")
    except Exception as e:
        pass

find_files('/public_html')
find_files('/kusum')
ftp.quit()

