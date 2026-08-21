"""
Inspect all php files in /public_html/kusum/Whatsapp_Rem/ via FTP
"""
import ftplib

ftp_host = 'ftp.sunfragroup.com'
ftp_user = 'u632391467.kusum1'
ftp_pass = 'h3>R~fQ*z?m'

ftp = ftplib.FTP()
ftp.connect(ftp_host, 21, timeout=30)
ftp.login(ftp_user, ftp_pass)
ftp.set_pasv(True)

def check_dir(dir_path):
    print(f"\n=== LISTING FILES IN {dir_path} ===")
    try:
        ftp.cwd(dir_path)
        files = ftp.nlst()
        print("Files:", files)
        for f in files:
            if f.endswith('.php'):
                # Download first 20 lines
                lines = []
                ftp.retrlines(f'RETR {f}', lambda line: lines.append(line))
                code_snippet = "\n".join(lines[:15])
                print(f"\n--- {dir_path}/{f} ---")
                print(code_snippet[:300])
    except Exception as e:
        print(f"Error in {dir_path}: {e}")

check_dir('/public_html/kusum/Whatsapp_Rem')
check_dir('/public_html/kusum/Whatsapp_Rem/frontend')
check_dir('/public_html')

ftp.quit()
