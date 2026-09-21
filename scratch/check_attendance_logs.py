import sys

sys.path.append('backend')
from database import get_db_session
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

db = get_db_session()

print("================ CHECKING SUNFRA_ATTENDANCE_LOGS TABLE SCHEMA & DATA ================")

try:
    res = db.execute(text("DESCRIBE sunfra_attendance_logs;")).fetchall()
    print("Columns in sunfra_attendance_logs:")
    for col in res:
        print(" ", col[0], col[1])
except Exception as e:
    print("Describe error:", e)

print("\n--- 16 SEP 2026 RECORDS ---")
try:
    rows_16 = db.execute(text("SELECT * FROM sunfra_attendance_logs WHERE date = '2026-09-16'")).fetchall()
    print(f"Total 16 Sep records: {len(rows_16)}")
    for r in rows_16:
        print(r)
except Exception as e:
    print("Error 16 sep:", e)

print("\n--- 17 SEP 2026 RECORDS ---")
try:
    rows_17 = db.execute(text("SELECT * FROM sunfra_attendance_logs WHERE date = '2026-09-17'")).fetchall()
    print(f"Total 17 Sep records: {len(rows_17)}")
    for r in rows_17:
        print(r)
except Exception as e:
    print("Error 17 sep:", e)

db.close()
