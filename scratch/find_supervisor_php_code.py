"""
Find and read the PHP source code of the 3 supervisor endpoints on FTP!
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

target_files = [
    'supervisor_shead_mortality_json_to_web.php',
    'supervisor_shead_production_json_to_web.php',
    'supervisor_birds_weight_json_to_web.php'
]

found_paths = {}

def scan_ftp(dir_path):
    try:
        ftp.cwd(dir_path)
        items = []
        ftp.retrlines('LIST', items.append)
        for item in items:
            parts = item.split()
            if not parts: continue
            name = parts[-1]
            is_dir = item.startswith('d')
            full_path = (dir_path.rstrip('/') + '/' + name).replace('//', '/')
            if is_dir:
                if name not in ['.', '..', '.git', '.well-known']:
                    scan_ftp(full_path)
            else:
                if name in target_files:
                    found_paths[name] = full_path
                    print(f"FOUND: {name} at {full_path} ✅")
    except Exception as e:
        pass

scan_ftp('/')

for fname, fpath in found_paths.items():
    print(f"\n==================== READING {fname} ({fpath}) ====================")
    try:
        content = []
        ftp.retrlines(f'RETR {fpath}', content.append)
        code = '\n'.join(content)
        print(code[:2000])
        with open(fr'c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\{fname}', 'w', encoding='utf-8') as out:
            out.write(code)
    except Exception as e:
        print(f"Error reading {fpath}: {e}")

ftp.quit()

