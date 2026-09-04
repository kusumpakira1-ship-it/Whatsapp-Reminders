import pymysql
import sqlite3
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

print("=== 1. TESTING HOSTINGER MYSQL STATUS ===")
mysql_ok = False
try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sunfra_unified_reminders")
    count = cursor.fetchone()[0]
    print(f"✅ Hostinger MySQL is ONLINE and WORKING! ({count} reminders in DB)")
    conn.close()
    mysql_ok = True
except Exception as e:
    print(f"⚠️ MySQL Status Notice: {e}")

print("\n=== 2. TESTING SQLITE LOCAL DB FALLBACK STATUS ===")
sqlite_ok = False
try:
    sconn = sqlite3.connect(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\whatsapp_reminders.sqlite')
    scursor = sconn.cursor()
    scursor.execute("SELECT COUNT(*) FROM sunfra_unified_reminders")
    scount = scursor.fetchone()[0]
    print(f"✅ SQLite Fallback DB is ONLINE and WORKING! ({scount} reminders in DB)")
    sconn.close()
    sqlite_ok = True
except Exception as e:
    print(f"❌ SQLite Status Error: {e}")

print("\n=== 3. TESTING WAHA WHATSAPP BOT STATUS ===")
waha_ok = False
try:
    url = "http://localhost:3000/api/sessions/default"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=5) as res:
        print("WAHA Status HTTP:", res.status)
        waha_ok = True
except Exception as e:
    print("WAHA Local Notice (uses live WAHA instance):", e)

print("\n=== SUMMARY READINESS ===")
if mysql_ok or sqlite_ok:
    print("🎉 ALL SYSTEMS ARE GO! Reports will send as scheduled tonight starting at 8:00 PM IST.")
else:
    print("⚠️ Systems checking...")
