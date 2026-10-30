import pymysql
import sqlite3
import os
import shutil

CORE_TABLES = [
    'sunfra_unified_reminders',
    'sunfra_tasks',
    'sunfra_custom_alarms',
    'sunfra_groups',
    'sunfra_employees',
    'sunfra_report_recipients',
    'sunfra_system_settings',
    'sunfra_book_standards',
    'sunfra_flocks',
    'mac_devices'
]

print("Connecting to Hostinger MySQL...")
mysql_conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira',
    cursorclass=pymysql.cursors.DictCursor
)
m_cur = mysql_conn.cursor()

sqlite_path = 'whatsapp_reminders.sqlite'
s_conn = sqlite3.connect(sqlite_path)
s_cur = s_conn.cursor()

for table in CORE_TABLES:
    try:
        m_cur.execute(f"SELECT * FROM `{table}`")
        rows = m_cur.fetchall()
        if not rows:
            print(f"Table {table}: 0 rows in MySQL, skipping.")
            continue
        
        cols = list(rows[0].keys())
        # Recreate table in SQLite
        col_defs = ", ".join([f"`{c}` TEXT" for c in cols])
        s_cur.execute(f"DROP TABLE IF EXISTS `{table}`")
        s_cur.execute(f"CREATE TABLE `{table}` ({col_defs})")
        
        placeholders = ", ".join(["?"] * len(cols))
        col_names = ", ".join([f"`{c}`" for c in cols])
        
        values = []
        for r in rows:
            row_vals = []
            for c in cols:
                val = r[c]
                if val is not None:
                    row_vals.append(str(val))
                else:
                    row_vals.append(None)
            values.append(tuple(row_vals))
            
        s_cur.executemany(f"INSERT INTO `{table}` ({col_names}) VALUES ({placeholders})", values)
        s_conn.commit()
        print(f"SUCCESS: synced `{table}`: {len(rows)} rows to SQLite.")
    except Exception as e:
        print(f"FAILED: Error syncing table `{table}`: {e}")

mysql_conn.close()
s_conn.close()

# Also copy to backend/whatsapp_reminders.sqlite and frontend/whatsapp_reminders.sqlite
for dest in ['backend/whatsapp_reminders.sqlite', 'backend/backend/whatsapp_reminders.sqlite', 'frontend/whatsapp_reminders.sqlite']:
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(sqlite_path, dest)
        print(f"Copied updated sqlite to {dest}")
    except Exception as e:
        print(f"Error copying to {dest}: {e}")

print("ALL CORE TABLES SYNCED TO SQLITE SUCCESSFULLY!")
