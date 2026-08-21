"""
Query Hostinger MySQL to find submission logs, tables, and why sub-reports weren't marked green for 2026-08-13.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

try:
    conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    print("Connected to Hostinger MySQL successfully!")
    
    # 1. Show all tables
    cursor.execute("SHOW TABLES")
    tables = [list(r.values())[0] for r in cursor.fetchall()]
    print("\nTables in DB:", tables)
    
    # 2. Inspect tables that might hold submission logs or report logs
    for t in tables:
        if 'report' in t or 'log' in t or 'sub' in t or 'file' in t or 'media' in t or 'waha' in t or 'reminder' in t:
            print(f"\n--- Table: {t} ---")
            cursor.execute(f"DESCRIBE {t}")
            cols = [c['Field'] for c in cursor.fetchall()]
            print("Columns:", cols)
            
            cursor.execute(f"SELECT COUNT(*) as count FROM {t}")
            cnt = cursor.fetchone()['count']
            print(f"Row count: {cnt}")
            
            # Fetch recent rows if any
            if cnt > 0:
                cursor.execute(f"SELECT * FROM {t} ORDER BY 1 DESC LIMIT 10")
                rows = cursor.fetchall()
                print("Recent rows:", json.dumps(rows, default=str, indent=2)[:1500])

except Exception as e:
    print("MySQL Error:", e)

