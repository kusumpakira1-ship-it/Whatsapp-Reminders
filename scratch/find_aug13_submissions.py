"""
Search all MySQL tables for 'Purchases by Vendor' or '21:03:27' or 'Day Book' from Aug 13.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
tables = [list(r.values())[0] for r in cursor.fetchall()]

for t in tables:
    try:
        cursor.execute(f"SELECT * FROM {t} WHERE CONCAT('', `id`) LIKE '%Purchases%' OR CONCAT('', `id`) LIKE '%Vendor%'")
    except:
        pass
    
    # Search text columns
    try:
        cursor.execute(f"DESCRIBE {t}")
        cols = cursor.fetchall()
        text_cols = [c['Field'] for c in cols if 'varchar' in c['Type'].lower() or 'text' in c['Type'].lower() or 'json' in c['Type'].lower()]
        if text_cols:
            where_clause = " OR ".join([f"`{col}` LIKE '%Purchases%' OR `{col}` LIKE '%21:03%' OR `{col}` LIKE '%Receivables%'" for col in text_cols])
            query = f"SELECT * FROM {t} WHERE {where_clause}"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows:
                print(f"\nFOUND MATCHES IN TABLE: {t} ({len(rows)} rows)")
                for r in rows[:5]:
                    print(r)
    except Exception as e:
        # print(f"Error in {t}: {e}")
        pass

