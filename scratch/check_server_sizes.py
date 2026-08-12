import ftplib, io

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)
ftp.sendcmd('TYPE I')  # Switch to binary mode for SIZE command

paths_to_check = [
    '/public_html/kusum/Whatsapp_Rem/frontend/index.php',
    '/public_html/kusum/Whatsapp_Rem/index.php',
    '/public_html/frontend/index.php',
    '/public_html/index.php',
]

print('File sizes on server (binary mode):')
for path in paths_to_check:
    dir_path = '/'.join(path.split('/')[:-1])
    filename = path.split('/')[-1]
    try:
        ftp.cwd(dir_path)
        size = ftp.size(filename)
        print(f'  {size:>8} bytes  {path}')
    except Exception as e:
        # Try reading first 100 bytes
        try:
            buf = io.BytesIO()
            ftp.retrbinary(f'RETR {filename}', buf.write, blocksize=8192)
            print(f'  {len(buf.getvalue()):>8} bytes  {path} (read full)')
        except Exception as e2:
            print(f'  ERROR: {e2}  {path}')

ftp.quit()
