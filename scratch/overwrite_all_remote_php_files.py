"""
Overwrite ALL remote PHP entrypoint files using BytesIO
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import ftplib
import pymysql
import io

print("=== 1. PURGING ALL WATER MONITORING ROWS FROM HOSTINGER MYSQL ===")
try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    sql_purge = """
    DELETE FROM sunfra_unified_reminders 
    WHERE LOWER(COALESCE(person_name,'')) LIKE '%water%' 
       OR LOWER(COALESCE(report_types,'')) LIKE '%water%' 
       OR LOWER(COALESCE(task_notes,'')) LIKE '%water%' 
       OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%120363409544891824%'
       OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%water%'
    """
    count = cursor.execute(sql_purge)
    conn.commit()
    print(f"Purged {count} Water Monitoring System rows from Hostinger MySQL!")
    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")

print("\n=== 2. OVERWRITING ALL ENTRYPOINT PHP FILES ON HOSTINGER SERVER ===")
ftp_host = 'ftp.sunfragroup.com'
ftp_user = 'u632391467.kusum1'
ftp_pass = 'h3>R~fQ*z?m'

local_index = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'
local_frontend_index = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'

with open(local_index, 'rb') as f:
    index_bytes = f.read()

with open(local_frontend_index, 'rb') as f:
    frontend_bytes = f.read()

target_remote_paths = [
    # /public_html/kusum/Whatsapp_Rem/
    ('/public_html/kusum/Whatsapp_Rem/index.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/index1.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/reminders.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/dashboard.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/app.php', index_bytes),

    # /public_html/kusum/Whatsapp_Rem/frontend/
    ('/public_html/kusum/Whatsapp_Rem/frontend/index.php', frontend_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/index1.php', frontend_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/reminders.php', frontend_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/dashboard.php', frontend_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/app.php', frontend_bytes),

    # /public_html/
    ('/public_html/index.php', index_bytes),
    ('/public_html/frontend/index.php', frontend_bytes)
]

try:
    ftp = ftplib.FTP()
    ftp.connect(ftp_host, 21, timeout=30)
    ftp.login(ftp_user, ftp_pass)
    ftp.set_pasv(True)

    for remote_path, data in target_remote_paths:
        try:
            ftp.storbinary(f'STOR {remote_path}', io.BytesIO(data))
            print(f"Uploaded {len(data)} bytes -> {remote_path} ✅")
        except Exception as fe:
            print(f"Error uploading {remote_path}: {fe}")

    ftp.quit()
    print("\nFTP Sync & Overwrite Complete across ALL PHP Entrypoints!")
except Exception as e:
    print(f"FTP Error: {e}")
