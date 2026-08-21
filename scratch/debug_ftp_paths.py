"""
Inspect exact FTP directory tree for FTP user u632391467.kusum1.
"""
import ftplib, sys
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

print("--- FTP CURRENT WORKING DIRECTORY ---")
pwd = ftp.pwd()
print(f"PWD: {pwd}")

print("\n--- LIST OF FILES IN ROOT ---")
ftp.retrlines('LIST')

print("\n--- TRYING LIST IN Whatsapp_Rem ---")
try:
    ftp.cwd('Whatsapp_Rem')
    print(f"PWD in Whatsapp_Rem: {ftp.pwd()}")
    ftp.retrlines('LIST')
except Exception as e:
    print(f"Error CWD Whatsapp_Rem: {e}")

print("\n--- TRYING LIST IN Whatsapp_Rem/frontend ---")
try:
    ftp.cwd('frontend')
    print(f"PWD in Whatsapp_Rem/frontend: {ftp.pwd()}")
    ftp.retrlines('LIST')
except Exception as e:
    print(f"Error CWD frontend: {e}")

ftp.quit()
