"""
Inspect exact sender details for Day book message at 18:57:27.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SELECT * FROM sunfra_whatsapp_messages WHERE message_text LIKE '%%Day book%%'")
msgs = cursor.fetchall()
for m in msgs:
    print(m)

conn.close()

