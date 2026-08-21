"""
Download current index.php from FTP and check if it has our new functions
"""
import ftplib, sys, io
sys.stdout.reconfigure(encoding='utf-8')

ftp = ftplib.FTP()
ftp.connect('ftp.sunfragroup.com', 21, timeout=30)
ftp.login('u632391467.kusum1', 'h3>R~fQ*z?m')
ftp.set_pasv(True)

buf = io.BytesIO()
ftp.cwd('/public_html/kusum/Whatsapp_Rem/frontend')
ftp.retrbinary('RETR index.php', buf.write)
ftp.quit()

content = buf.getvalue().decode('utf-8', errors='ignore')
print(f"FTP Downloaded file size: {len(content)} chars")
print(f"Has 'confirmToggleSubReport': {'YES ✅' if 'confirmToggleSubReport' in content else 'NO ❌'}")
print(f"Has 'resetAllSubReports': {'YES ✅' if 'resetAllSubReports' in content else 'NO ❌'}")
print(f"Has 'sub_reports_status': {'YES ✅' if 'sub_reports_status' in content else 'NO ❌'}")
print(f"Has 'Undone': {'YES ✅' if 'Undone' in content else 'NO ❌'}")
print(f"Has 'BUILD_TAG': {'YES ✅' if 'BUILD_TAG' in content else 'NO ❌'}")
