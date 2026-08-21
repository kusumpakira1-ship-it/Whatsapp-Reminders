"""
Purge Supervisors tasks from SQLite backup and upload via FTP
"""
import sqlite3
import ftplib

sqlite_file = r"c:\Users\sunfra\Desktop\Whatsapp New Reminders\whatsapp_reminders.sqlite"
conn = sqlite3.connect(sqlite_file)
cursor = conn.cursor()

cursor.execute("DELETE FROM sunfra_tasks WHERE assigned_person_name = 'Supervisors' OR id IN (114, 115, 116, 117, 118)")
conn.commit()
conn.close()
print("Purged Supervisors tasks from local SQLite!")

print("=== UPLOADING UPDATED SQLITE TO HOSTINGER VIA FTP ===")
ftp_host = 'ftp.sunfragroup.com'
ftp_user = 'u632391467.kusum1'
ftp_pass = 'h3>R~fQ*z?m'

try:
    ftp = ftplib.FTP()
    ftp.connect(ftp_host, 21, timeout=30)
    ftp.login(ftp_user, ftp_pass)
    ftp.set_pasv(True)

    upload_map = [
        ('/public_html/kusum/Whatsapp_Rem/whatsapp_reminders.sqlite', sqlite_file),
        ('/public_html/kusum/Whatsapp_Rem/frontend/whatsapp_reminders.sqlite', sqlite_file),
        ('/public_html/whatsapp_reminders.sqlite', sqlite_file)
    ]

    for remote_path, local_path in upload_map:
        try:
            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)
            print(f"Uploaded {local_path} -> {remote_path}")
        except Exception as e:
            print(f"Error uploading {remote_path}: {e}")

    ftp.quit()
    print("FTP Sync Complete!")
except Exception as e:
    print(f"FTP Error: {e}")
