import sys, os, pymysql
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)

cur = conn.cursor(pymysql.cursors.DictCursor)

cur.execute("SHOW TABLES")
tables = [list(r.values())[0] for r in cur.fetchall()]
print(f"=== HOSTINGER TABLES ({len(tables)}) ===")
print(tables)

for t in tables:
    if 'reminder' in t or 'task' in t or 'report' in t or 'schedule' in t:
        try:
            cur.execute(f"SELECT * FROM {t} WHERE 1")
            rows = cur.fetchall()
            print(f"\n--- TABLE {t} ({len(rows)} rows) ---")
            for r in rows:
                r_str = str(r).lower()
                if 'gate' in r_str or 'meeting' in r_str or 'worker' in r_str:
                    print(f"  MATCH IN {t}: {r}")
        except Exception as e:
            print(f"Error reading {t}: {e}")

cur.close()
conn.close()
