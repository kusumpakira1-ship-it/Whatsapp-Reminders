import sqlite3

con = sqlite3.connect(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\whatsapp_reminders.sqlite')
cur = con.cursor()
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables in backend sqlite:', len(tables))
for t in tables:
    tname = t[0]
    try:
        cnt = cur.execute(f'SELECT count(*) FROM "{tname}"').fetchone()[0]
        print(f'Table {tname}: {cnt} rows')
    except Exception as e:
        print(f'Table {tname}: ERROR {e}')
con.close()
