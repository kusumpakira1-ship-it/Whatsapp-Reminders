"""
Inspect subfolders under /public_html/kusum
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("--- LIST OF /public_html/kusum ---")
ftp.cwd('/public_html/kusum')
ftp.retrlines('LIST')

print("\n--- LIST OF /public_html/kusum/Whatsapp_Rem ---")
try:
    ftp.cwd('/public_html/kusum/Whatsapp_Rem')
    ftp.retrlines('LIST')
except Exception as e:
    print(f"Error: {e}")

print("\n--- LIST OF /public_html/kusum/Whatsapp_Rem/frontend ---")
try:
    ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
    ftp.retrlines('LIST')
except Exception as e:
    print(f"Error: {e}")

ftp.quit()
