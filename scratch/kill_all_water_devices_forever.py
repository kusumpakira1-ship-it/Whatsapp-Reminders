"""
Purge ALL Water Device alerts (including Power Status is OFF, MAC, Location, etc.) and update index.php / frontend/index.php
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import pymysql
import ftplib
import io

print("=== 1. PURGING ALL WATER & DEVICE ALERTS FROM HOSTINGER MYSQL ===")
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
       OR LOWER(COALESCE(task_notes,'')) LIKE '%mac:%'
       OR LOWER(COALESCE(task_notes,'')) LIKE '%location:%'
       OR LOWER(COALESCE(task_notes,'')) LIKE '%power status%'
       OR LOWER(COALESCE(task_notes,'')) LIKE '%alert%'
       OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%120363409544891824%'
       OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%water%'
       OR LOWER(COALESCE(whatsapp_group_id,'')) LIKE '%lid%'
    """
    count = cursor.execute(sql_purge)
    conn.commit()
    print(f"Purged {count} Water Monitoring System & Device Alert rows from Hostinger MySQL!")
    conn.close()
except Exception as e:
    print(f"MySQL Error: {e}")

print("\n=== 2. UPDATING LOCAL INDEX.PHP AND FRONTEND/INDEX.PHP WITH BULLETPROOF DEVICE FILTER ===")
local_index = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\index.php'
local_frontend_index = r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\frontend\index.php'

old_sql = "$stmt = $pdo->query(\"SELECT * FROM sunfra_unified_reminders WHERE (LOWER(COALESCE(person_name,'')) NOT LIKE '%water%' AND LOWER(COALESCE(report_types,'')) NOT LIKE '%water%' AND LOWER(COALESCE(task_notes,'')) NOT LIKE '%water%' AND LOWER(COALESCE(whatsapp_group_id,'')) NOT LIKE '%water%' AND LOWER(COALESCE(whatsapp_group_id,'')) NOT LIKE '%120363409544891824%') ORDER BY trigger_time DESC\");"

new_sql = "$stmt = $pdo->query(\"SELECT * FROM sunfra_unified_reminders WHERE (LOWER(COALESCE(person_name,'')) NOT LIKE '%water%' AND LOWER(COALESCE(report_types,'')) NOT LIKE '%water%' AND LOWER(COALESCE(task_notes,'')) NOT LIKE '%water%' AND LOWER(COALESCE(task_notes,'')) NOT LIKE '%mac:%' AND LOWER(COALESCE(task_notes,'')) NOT LIKE '%location:%' AND LOWER(COALESCE(task_notes,'')) NOT LIKE '%power status%' AND LOWER(COALESCE(whatsapp_group_id,'')) NOT LIKE '%water%' AND LOWER(COALESCE(whatsapp_group_id,'')) NOT LIKE '%120363409544891824%' AND LOWER(COALESCE(whatsapp_group_id,'')) NOT LIKE '%lid%') ORDER BY trigger_time DESC\");"

old_post_check = "if (strpos($pname, 'water') !== false || strpos($rtypes, 'water') !== false || strpos($notes, 'water') !== false || strpos($gid, 'water') !== false || strpos($gid, '120363409544891824') !== false)"

new_post_check = "if (strpos($pname, 'water') !== false || strpos($rtypes, 'water') !== false || strpos($notes, 'water') !== false || strpos($notes, 'mac:') !== false || strpos($notes, 'location:') !== false || strpos($notes, 'power status') !== false || strpos($gid, 'water') !== false || strpos($gid, '120363409544891824') !== false || strpos($gid, 'lid') !== false)"

old_js_check = "if (pNameLower.includes('water') || rTypesLower.includes('water') || notesLower.includes('water') || gNameLower.includes('water') || gIdLower.includes('water') || gIdLower.includes('120363409544891824')) return;"

new_js_check = "if (pNameLower.includes('water') || rTypesLower.includes('water') || notesLower.includes('water') || notesLower.includes('mac:') || notesLower.includes('location:') || notesLower.includes('power status') || gNameLower.includes('water') || gIdLower.includes('water') || gIdLower.includes('120363409544891824') || gIdLower.includes('lid')) return;"

for fpath in [local_index, local_frontend_index]:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    if old_sql in content:
        content = content.replace(old_sql, new_sql)
    if old_post_check in content:
        content = content.replace(old_post_check, new_post_check)
    if old_js_check in content:
        content = content.replace(old_js_check, new_js_check)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated device filters in {fpath}")

print("\n=== 3. OVERWRITING ALL 12 PHP ENTRYPOINTS ON HOSTINGER VIA FTP ===")
ftp_host = 'ftp.sunfragroup.com'
ftp_user = 'u632391467.kusum1'
ftp_pass = 'h3>R~fQ*z?m'

with open(local_index, 'rb') as f:
    index_bytes = f.read()

with open(local_frontend_index, 'rb') as f:
    frontend_bytes = f.read()

target_remote_paths = [
    ('/public_html/kusum/Whatsapp_Rem/index.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/index1.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/reminders.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/dashboard.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/app.php', index_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/index.php', frontend_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/index1.php', frontend_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/reminders.php', frontend_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/dashboard.php', frontend_bytes),
    ('/public_html/kusum/Whatsapp_Rem/frontend/app.php', frontend_bytes),
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
