"""
Script to list exact present age in days and weeks for all sheds
"""

import sys, os, pymysql, datetime
sys.stdout.reconfigure(encoding='utf-8')

conn = pymysql.connect(
    host='145.223.17.70',
    user='u632391467_kusumpakira',
    password='Kusum@2026Bb!',
    database='u632391467_kusumpakira'
)
cur = conn.cursor(pymysql.cursors.DictCursor)

today = datetime.date.today()

cur.execute("SELECT shed_name, hatch_date, live_birds, status FROM sunfra_flocks ORDER BY id")
flocks = cur.fetchall()

print(f"=== PRESENT AGE OF ALL BIRDS & SHEDS (AS OF TODAY: {today.strftime('%d %b %Y')}) ===")
for f in flocks:
    hatch = f['hatch_date']
    status = f['status']
    if hatch:
        days = (today - hatch).days + 1
        weeks = (days - 1) // 7 + 1
        birds = f['live_birds'] or 0
        print(f"• {f['shed_name']:<10}: Age = Day {days:3d} (Week {weeks:2d}) | Hatch Date = {hatch.strftime('%d %b %Y')} | Live Birds = {birds:,} [{status.upper()}]")

cur.close()
conn.close()
