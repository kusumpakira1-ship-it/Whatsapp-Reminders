"""
Deploy updated index.php and clean DB on Hostinger via FTP and MySQL
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import ftplib
import pymysql
import os

print("=== 1. CLEANING HOSTINGER MYSQL DATABASE ===")
try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    sql_del = """
    DELETE FROM sunfra_unified_reminders 
    WHERE LOWER(person_name) LIKE '%water%' 
       OR LOWER(report_types) LIKE '%water%' 
       OR LOWER(task_notes) LIKE '%water%' 
       OR LOWER(whatsapp_group_id) LIKE '%120363409544891824%'
       OR LOWER(whatsapp_group_id) LIKE '%water%'
    """
    affected = cursor.execute(sql_del)
    conn.commit()
    print(f"Deleted {affected} Water Monitoring System rows from Hostinger MySQL!")
    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")

print("\n=== 2. UPLOADING UPDATED INDEX.PHP TO HOSTINGER VIA FTP ===")
ftp_host = 'ftp.sunfragroup.com'
ftp_user = 'u632391467.kusum1'
ftp_pass = 'h3>R~fQ*z?m'

local_index = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'
local_frontend_index = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'

try:
    ftp = ftplib.FTP()
    ftp.connect(ftp_host, 21, timeout=30)
    ftp.login(ftp_user, ftp_pass)
    ftp.set_pasv(True)
    print("FTP Connected successfully!")

    target_files = [
        ('/public_html/kusum/Whatsapp_Rem/index.php', local_index),
        ('/public_html/kusum/Whatsapp_Rem/index1.php', local_index),
        ('/public_html/kusum/Whatsapp_Rem/frontend/index.php', local_frontend_index),
        ('/public_html/index.php', local_index)
    ]

    for remote_path, local_path in target_files:
        try:
            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {remote_path}', f)
            print(f"Successfully uploaded {local_path} -> {remote_path}")
        except Exception as fe:
            print(f"Error uploading to {remote_path}: {fe}")

    ftp.quit()
    print("FTP Deployment Complete!")
except Exception as e:
    print(f"FTP Error: {e}")
