"""
Read .htaccess files from all directories on Hostinger via FTP
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

def read_remote_file(path):
    print(f"\n--- READING {path} ---")
    lines = []
    try:
        ftp.retrlines(f'RETR {path}', lines.append)
        print("\n".join(lines))
    except Exception as e:
        print(f"Error reading {path}: {e}")

read_remote_file('/public_html/.htaccess')
read_remote_file('/public_html/kusum/.htaccess')
read_remote_file('/public_html/kusum/Whatsapp_Rem/.htaccess')
read_remote_file('/public_html/kusum/Whatsapp_Rem/frontend/.htaccess')

ftp.quit()
