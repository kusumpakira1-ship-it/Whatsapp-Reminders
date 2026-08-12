import ftplib, io, time

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')

# Read current index.php from server
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
buf = io.BytesIO()
ftp.retrbinary('RETR index.php', buf.write)
content = buf.getvalue()

# Write a temp PHP file that clears OPcache
clear_opcache_php = b"<?php\nif (function_exists('opcache_reset')) {\n    opcache_reset();\n    echo 'OPcache cleared!';\n} else {\n    echo 'opcache_reset not available';\n}\n?>"

paths = [
    '/public_html/kusum/Whatsapp_Rem',
    '/public_html/kusum/Whatsapp_Rem/frontend',
    '/public_html',
    '/public_html/frontend'
]

for path in paths:
    try:
        ftp.cwd(path)
        ftp.storbinary('STOR __clear_cache.php', io.BytesIO(clear_opcache_php))
        print(f'Uploaded __clear_cache.php to {path}')
    except Exception as e:
        print(f'Failed at {path}: {e}')

ftp.quit()
print('Done! Now visit these URLs to trigger cache clear:')
for p in paths:
    print(f'  https://sunfragroup.com{p.replace("/public_html", "")}/__clear_cache.php')
