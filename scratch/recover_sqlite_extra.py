import sqlite3
import os

src_path = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\whatsapp_reminders.sqlite'
dst_path = r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\whatsapp_reminders_recovered.sqlite'

src = sqlite3.connect(src_path)
dst = sqlite3.connect(dst_path)

src_cur = src.cursor()
dst_cur = dst.cursor()

# Get max rowid of sunfra_raw_messages
max_rowid = src_cur.execute("SELECT max(rowid) FROM sunfra_raw_messages").fetchone()[0] or 0
print(f"Max rowid in sunfra_raw_messages: {max_rowid}")

# Find which rowids are missing in dst
existing_ids = set(r[0] for r in dst_cur.execute("SELECT id FROM sunfra_raw_messages").fetchall())
print(f"Already recovered in dst: {len(existing_ids)}")

recovered_extra = 0
failed_pages = 0

batch = []
for rid in range(1, max_rowid + 1):
    if rid in existing_ids:
        continue
    try:
        row = src_cur.execute(f"SELECT * FROM sunfra_raw_messages WHERE rowid = {rid}").fetchone()
        if row:
            batch.append(row)
            if len(batch) >= 100:
                placeholders = ','.join(['?'] * len(batch[0]))
                dst_cur.executemany(f'INSERT OR IGNORE INTO sunfra_raw_messages VALUES ({placeholders})', batch)
                dst.commit()
                recovered_extra += len(batch)
                batch = []
    except Exception as e:
        failed_pages += 1

if batch:
    placeholders = ','.join(['?'] * len(batch[0]))
    dst_cur.executemany(f'INSERT OR IGNORE INTO sunfra_raw_messages VALUES ({placeholders})', batch)
    dst.commit()
    recovered_extra += len(batch)

print(f"Extra recovered rows: {recovered_extra}, failed rowids: {failed_pages}")

# Same for sunfra_papaak_egg_rates
max_rid_papaak = src_cur.execute("SELECT max(rowid) FROM sunfra_papaak_egg_rates").fetchone()[0] or 0
existing_papaak = set(r[0] for r in dst_cur.execute("SELECT id FROM sunfra_papaak_egg_rates").fetchall())
extra_papaak = 0
batch_p = []
for rid in range(1, max_rid_papaak + 1):
    if rid in existing_papaak:
        continue
    try:
        row = src_cur.execute(f"SELECT * FROM sunfra_papaak_egg_rates WHERE rowid = {rid}").fetchone()
        if row:
            batch_p.append(row)
            if len(batch_p) >= 100:
                placeholders = ','.join(['?'] * len(batch_p[0]))
                dst_cur.executemany(f'INSERT OR IGNORE INTO sunfra_papaak_egg_rates VALUES ({placeholders})', batch_p)
                dst.commit()
                extra_papaak += len(batch_p)
                batch_p = []
    except Exception as e:
        pass

if batch_p:
    placeholders = ','.join(['?'] * len(batch_p[0]))
    dst_cur.executemany(f'INSERT OR IGNORE INTO sunfra_papaak_egg_rates VALUES ({placeholders})', batch_p)
    dst.commit()
    extra_papaak += len(batch_p)

print(f"Extra recovered papaak: {extra_papaak}")

dst_cur.execute("PRAGMA integrity_check")
print("Integrity check:", dst_cur.fetchall())

# Check today's messages in recovered DB
today_count = dst_cur.execute("SELECT count(*), min(timestamp), max(timestamp) FROM sunfra_raw_messages WHERE timestamp >= '2026-10-16'").fetchone()
print("Today's messages in recovered DB:", today_count)

src.close()
dst.close()
