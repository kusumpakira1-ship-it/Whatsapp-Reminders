import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('whatsapp_reminders.sqlite')
cursor = conn.cursor()

print("=== SUNFRA PAPAAK EGG RATES ===")
cursor.execute("SELECT * FROM sunfra_papaak_egg_rates ORDER BY id DESC")
rows = cursor.fetchall()
cols = [d[0] for d in cursor.description]
print(f"Columns: {cols}")
print(f"Total rows in sunfra_papaak_egg_rates: {len(rows)}")
for r in rows:
    print(dict(zip(cols, r)))

print("\n=== SEARCHING ALL TABLES FOR 'PAPAAK' OR 'PAPA' ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

for t in tables:
    cursor.execute(f"PRAGMA table_info('{t}')")
    cols = [col[1] for col in cursor.fetchall()]
    
    where_clauses = [f"CAST({c} AS TEXT) LIKE '%papa%'" for c in cols]
    query = f"SELECT * FROM '{t}' WHERE {' OR '.join(where_clauses)}"
    try:
        cursor.execute(query)
        matches = cursor.fetchall()
        if matches:
            print(f"\nTable {t} matching 'papa': {len(matches)} rows")
            for m in matches[:10]:
                print(dict(zip(cols, m)))
    except Exception as e:
        pass
