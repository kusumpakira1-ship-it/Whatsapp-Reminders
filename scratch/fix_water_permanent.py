"""
Purge Water Monitoring rows and apply double-layer case-insensitive filter in index.php and frontend/index.php
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import pymysql
import ftplib

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

print("\n=== 2. UPDATING LOCAL INDEX.PHP AND FRONTEND/INDEX.PHP WITH DOUBLE-LAYER FILTER ===")
local_index = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'
local_frontend_index = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'

old_sql = "$stmt = $pdo->query(\"SELECT * FROM sunfra_unified_reminders WHERE (person_name NOT LIKE '%water%' AND report_types NOT LIKE '%water%' AND task_notes NOT LIKE '%water%' AND (whatsapp_group_id IS NULL OR whatsapp_group_id NOT LIKE '%120363409544891824%')) ORDER BY trigger_time DESC\");"

new_sql = "$stmt = $pdo->query(\"SELECT * FROM sunfra_unified_reminders WHERE (LOWER(COALESCE(person_name,'')) NOT LIKE '%water%' AND LOWER(COALESCE(report_types,'')) NOT LIKE '%water%' AND LOWER(COALESCE(task_notes,'')) NOT LIKE '%water%' AND LOWER(COALESCE(whatsapp_group_id,'')) NOT LIKE '%water%' AND LOWER(COALESCE(whatsapp_group_id,'')) NOT LIKE '%120363409544891824%') ORDER BY trigger_time DESC\");"

old_foreach = "foreach ($rows as &$row) {"
new_foreach = """foreach ($rows as $key => &$row) {
                $pname = strtolower($row['person_name'] ?? '');
                $rtypes = strtolower($row['report_types'] ?? '');
                $notes = strtolower($row['task_notes'] ?? '');
                $gid = strtolower($row['whatsapp_group_id'] ?? '');
                if (strpos($pname, 'water') !== false || strpos($rtypes, 'water') !== false || strpos($notes, 'water') !== false || strpos($gid, 'water') !== false || strpos($gid, '120363409544891824') !== false) {
                    unset($rows[$key]);
                    continue;
                }"""

for fpath in [local_index, local_frontend_index]:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_sql in content:
        content = content.replace(old_sql, new_sql)
    if old_foreach in content:
        content = content.replace(old_foreach, new_foreach)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated filters in {fpath}")

print("\n=== 3. UPLOADING ALL INDEX.PHP FILES TO HOSTINGER VIA FTP ===")
ftp_host = 'ftp.sunfragroup.com'
ftp_user = 'u632391467.kusum1'
ftp_pass = 'h3>R~fQ*z?m'

try:
    ftp = ftplib.FTP()
    ftp.connect(ftp_host, 21, timeout=30)
    ftp.login(ftp_user, ftp_pass)
    ftp.set_pasv(True)

    target_files = [
        ('/public_html/kusum/Whatsapp_Rem/index.php', local_index),
        ('/public_html/kusum/Whatsapp_Rem/index1.php', local_index),
        ('/public_html/kusum/Whatsapp_Rem/frontend/index.php', local_frontend_index),
        ('/public_html/index.php', local_index),
        ('/public_html/frontend/index.php', local_frontend_index)
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
