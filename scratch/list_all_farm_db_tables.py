"""
List all MySQL tables related to mortality, production, weight, supervisor, shed, flock.
"""
import pymysql, sys
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
tables = [list(t.values())[0] for t in cursor.fetchall()]

print("=== ALL TABLES IN MYSQL DATABASE ===")
for t in sorted(tables):
    if any(k in t.lower() for k in ['mortality', 'production', 'weight', 'supervisor', 'shed', 'flock', 'chick', 'egg', 'farm', 'book', 'standard', 'daily', 'entry']):
        print(" ->", t)

