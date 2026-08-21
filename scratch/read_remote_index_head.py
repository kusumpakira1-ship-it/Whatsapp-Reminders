"""
Read top 50 lines of /public_html/kusum/Whatsapp_Rem/index.php directly from Hostinger
"""
import ftplib

FTP_HOST = "ftp.sunfragroup.com"
FTP_USER = "u632391467.kusum1"
FTP_PASS = "h3>R~fQ*z?m"

ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
ftp.set_pasv(True)

data = bytearray()
ftp.retrbinary("RETR /public_html/kusum/Whatsapp_Rem/index.php", data.extend)
ftp.quit()

text = data.decode('utf-8', errors='ignore')
print("=== FIRST 1000 CHARACTERS OF REMOTE /public_html/kusum/Whatsapp_Rem/index.php ===")
print(text[:1000])
