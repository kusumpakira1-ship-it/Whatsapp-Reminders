"""
Download and check all PHP files on Hostinger FTP to see which file contains fetchReminders.
"""
import ftplib, sys, os
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

target_files = [
    '/public_html/kusum/Whatsapp_Rem/frontend/index.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/reminders.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/dashboard.php',
    '/public_html/kusum/Whatsapp_Rem/frontend/app.php',
    '/public_html/kusum/Whatsapp_Rem/reminders.php',
    '/public_html/kusum/Whatsapp_Rem/app.php',
    '/public_html/kusum/Whatsapp_Rem/dashboard.php',
    '/public_html/kusum/index.php',
    '/public_html/index.php'
]

os.makedirs(r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\ftp_download", exist_ok=True)

for remote in target_files:
    fname = os.path.basename(remote)
    local_p = os.path.join(r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\ftp_download", f"{remote.replace('/', '_')}")
    try:
        with open(local_p, 'wb') as f:
            ftp.retrbinary(f'RETR {remote}', f.write)
        
        with open(local_p, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.read()
            print(f"File {remote:<55}: Length={len(txt)} | Has 'confirmToggleSubReport'={'confirmToggleSubReport' in txt} | Has 'fetchReminders'={'fetchReminders' in txt}")
    except Exception as e:
        print(f"File {remote:<55}: Notice {e}")

ftp.quit()

