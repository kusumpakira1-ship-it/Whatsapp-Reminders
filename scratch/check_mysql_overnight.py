import sys
import os
from datetime import datetime

# sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

try:
    import pymysql
except ImportError:
    print("pymysql not installed, trying mysql.connector")
    import mysql.connector as pymysql

DB_HOST = "145.223.17.70"
DB_NAME = "u632391467_kusumpakira"
DB_USER = "u632391467_kusumpakira"
DB_PASS = "Kusum@2026Bb!"

print(f"Connecting to MySQL DB {DB_HOST} / {DB_NAME}...")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        connect_timeout=10
    )
    cursor = conn.cursor()
    print("Connected to MySQL successfully!")

    cursor.execute("SHOW TABLES;")
    tables = [r[0] for r in cursor.fetchall()]
    print("MySQL Tables:", tables)

    for table in tables:
        # Check column names
        cursor.execute(f"DESCRIBE `{table}`")
        cols = [c[0] for c in cursor.fetchall()]
        time_cols = [c for c in cols if 'time' in c.lower() or 'created' in c.lower() or 'updated' in c.lower() or 'date' in c.lower() or 'timestamp' in c.lower()]
        
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        count = cursor.fetchone()[0]
        print(f"\n--- MySQL Table: `{table}` (Total Rows: {count}) ---")

        for tcol in time_cols:
            try:
                cursor.execute(f"SELECT MIN(`{tcol}`), MAX(`{tcol}`) FROM `{table}`")
                res = cursor.fetchone()
                print(f"  Col [{tcol}] Min: {res[0]} | Max: {res[1]}")

                cursor.execute(f"SELECT COUNT(*) FROM `{table}` WHERE `{tcol}` >= '2026-09-28 20:00:00' AND `{tcol}` <= '2026-09-29 10:30:00'")
                cnt_range = cursor.fetchone()[0]
                print(f"  Col [{tcol}] Rows between Sept 28 20:00 & Sept 29 10:30: {cnt_range}")
            except Exception as e:
                print(f"  Col [{tcol}] error: {e}")

    conn.close()

except Exception as e:
    print(f"MySQL Connection/Query Error: {e}")
