import requests
import sqlite3
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')

print("=== 1. CHECK LOCAL WAHA CONTAINER / API ===")
for port in [3000, 2000, 8000]:
    try:
        r = requests.get(f"http://localhost:{port}/api/sessions", timeout=2)
        print(f"Port {port} WAHA sessions:", r.status_code, r.text[:200])
    except Exception as e:
        print(f"Port {port} reachability error: {e}")

print("\n=== 2. CHECK MYSQL WAHA EVENTS (LAST 10) ===")
try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, event_type, status, details FROM sunfra_waha_events ORDER BY id DESC LIMIT 10")
    for row in cursor.fetchall():
        print(f"MySQL Event ID: {row['id']} | TS: {row['timestamp']} | Type: {row['event_type']} | Status: {row['status']} | Details: {str(row['details'])[:60]}")
    conn.close()
except Exception as e:
    print("MySQL Error:", e)

print("\n=== 3. CHECK SQLITE WAHA EVENTS (LAST 10) ===")
try:
    sconn = sqlite3.connect("backend/whatsapp_reminders.sqlite")
    scursor = sconn.cursor()
    scursor.execute("SELECT id, timestamp, event_type, status, details FROM sunfra_waha_events ORDER BY id DESC LIMIT 10")
    for row in scursor.fetchall():
        print(f"SQLite Event ID: {row[0]} | TS: {row[1]} | Type: {row[2]} | Status: {row[3]} | Details: {str(row[4])[:60]}")
    sconn.close()
except Exception as e:
    print("SQLite Error:", e)
