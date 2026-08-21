"""
Find exact server filesystem path of https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php
"""

import ftplib, urllib.request, sys, time, io
sys.stdout.reconfigure(encoding='utf-8')

get_path_php = b"<?php echo 'REAL_PATH:' . __FILE__ . ' | REAL_DIR:' . __DIR__; ?>"

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

# Find all directories
def find_dirs(path):
    dirs = [path]
    try:
        ftp.cwd(path)
        items = ftp.nlst()
        for item in items:
            if item not in ['.', '..'] and not '.' in item:
                sub = path + '/' + item if path != '/' else '/' + item
                dirs.extend(find_dirs(sub))
    except Exception:
        pass
    return dirs

all_dirs = find_dirs('/')
print("All FTP Directories:", all_dirs)

for d in all_dirs:
    try:
        ftp.cwd(d)
        ftp.storbinary('STOR get_path.php', io.BytesIO(get_path_php))
    except Exception:
        pass

ftp.quit()

time.sleep(1)
res = urllib.request.urlopen('https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/get_path.php').read().decode('utf-8')
print("\nFETCHED FROM FRONTEND URL:", res)

res2 = urllib.request.urlopen('https://sunfragroup.com/kusum/Whatsapp_Rem/get_path.php').read().decode('utf-8')
print("FETCHED FROM ROOT URL:", res2)
