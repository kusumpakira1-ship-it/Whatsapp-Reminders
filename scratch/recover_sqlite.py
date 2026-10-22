import sqlite3
import os

src_path = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\whatsapp_reminders.sqlite'
dst_path = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\whatsapp_reminders_recovered.sqlite'

if os.path.exists(dst_path):
    os.remove(dst_path)

src = sqlite3.connect(src_path)
dst = sqlite3.connect(dst_path)

src_cur = src.cursor()
dst_cur = dst.cursor()

tables = src_cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()

for tname, create_sql in tables:
    if not create_sql:
        continue
    print(f"Processing table {tname}...")
    try:
        dst_cur.execute(create_sql)
        # Fetch rows from src
        src_cur.execute(f'SELECT * FROM "{tname}"')
        rows = []
        copied = 0
        while True:
            try:
                row = src_cur.fetchone()
                if row is None:
                    break
                rows.append(row)
                if len(rows) >= 500:
                    placeholders = ','.join(['?'] * len(rows[0]))
                    dst_cur.executemany(f'INSERT OR IGNORE INTO "{tname}" VALUES ({placeholders})', rows)
                    dst.commit()
                    copied += len(rows)
                    rows = []
            except Exception as row_err:
                print(f"  Row error in {tname}: {row_err}")
                break
        if rows:
            placeholders = ','.join(['?'] * len(rows[0]))
            dst_cur.executemany(f'INSERT OR IGNORE INTO "{tname}" VALUES ({placeholders})', rows)
            dst.commit()
            copied += len(rows)
        print(f"  Successfully copied {copied} rows for {tname}")
    except Exception as e:
        print(f"Error copying table {tname}: {e}")

# Copy indices
indices = src_cur.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL").fetchall()
for (idx_sql,) in indices:
    try:
        dst_cur.execute(idx_sql)
    except Exception as e:
        pass
dst.commit()

dst_cur.execute("PRAGMA integrity_check")
print("Recovered DB integrity check:", dst_cur.fetchall())

src.close()
dst.close()
