import sqlite3

src = sqlite3.connect(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend\whatsapp_reminders.sqlite')
cur = src.cursor()
try:
    res = cur.execute('SELECT count(*), max(id), max(timestamp) FROM sunfra_raw_messages WHERE timestamp >= "2026-10-16"').fetchall()
    print('Today messages query:', res)
except Exception as e:
    print('Error on today messages query:', e)

# Test querying max rowid
try:
    max_id = cur.execute('SELECT max(rowid) FROM sunfra_raw_messages').fetchone()[0]
    print('Max rowid:', max_id)
except Exception as e:
    print('Max rowid error:', e)

src.close()
