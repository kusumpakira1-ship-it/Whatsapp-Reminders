"""
Recursively search FTP for supervisor_shead_mortality_json_to_web.php.
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

def find_files(dir_path):
    print("Checking directory:", dir_path)
    try:
        ftp.cwd(dir_path)
        items = []
        ftp.dir(items.append)
        for line in items:
            parts = line.split()
            fname = parts[-1]
            if line.startswith('d') and fname not in ['.', '..']:
                find_files(f"{dir_path}/{fname}")
            elif 'mortality' in fname.lower() or 'production' in fname.lower() or 'supervisor' in fname.lower() or 'batch' in fname.lower():
                print(f"🎯 FOUND TARGET FILE: {dir_path}/{fname}")
    except Exception as e:
        print(f"Error reading {dir_path}: {e}")

find_files('/public_html')

ftp.quit()

