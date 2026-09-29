import sqlite3
import os
import sys
import requests
import json
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')
IST = timezone(timedelta(hours=5, minutes=30))

print(f"================ SYSTEM HEALTH & STATUS DIAGNOSTIC ================")
print(f"Local Time: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S IST')}\n")

# 1. Database Check
db_path = 'whatsapp_reminders.sqlite'
print(f"--- 1. DATABASE INTEGRITY & SUMMARY ({db_path}) ---")
if not os.path.exists(db_path):
    print("❌ ERROR: Database file whatsapp_reminders.sqlite not found!")
else:
    db_size = os.path.getsize(db_path) / 1024
    print(f"✓ Database File Exists (Size: {db_size:.2f} KB)")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check integrity
        cursor.execute("PRAGMA integrity_check;")
        res = cursor.fetchone()[0]
        print(f"✓ Database Integrity Check: {res}")

        # Check key tables row counts & recent updates
        tables = [
            'sunfra_unified_reminders',
            'sunfra_tasks',
            'sunfra_papaak_egg_rates',
            'sunfra_raw_messages',
            'sunfra_whatsapp_messages',
            'sunfra_reminder_logs',
            'sunfra_waha_events',
            'sunfra_attendance_logs',
            'sunfra_system_settings'
        ]
        
        print("\nTable Summary:")
        for t in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM '{t}'")
                cnt = cursor.fetchone()[0]
                print(f"  • {t}: {cnt} rows")
            except Exception as e:
                print(f"  • {t}: [Table missing or error: {e}]")
                
    except Exception as e:
        print(f"❌ Error inspecting SQLite database: {e}")

# 2. WAHA WhatsApp Session & API Check
print("\n--- 2. WAHA WHATSAPP SESSION STATUS ---")
waha_base_url = "http://localhost:3000"
try:
    resp = requests.get(f"{waha_base_url}/api/sessions", timeout=5)
    if resp.status_code == 200:
        sessions = resp.json()
        print(f"✓ WAHA Service API is Reachable (Status 200)")
        print(f"  Sessions found: {len(sessions)}")
        for s in sessions:
            name = s.get('name') or s.get('id')
            status = s.get('status')
            me = s.get('me', {})
            print(f"  • Session '{name}': Status = {status}, User = {me.get('id', 'N/A')}")
    else:
        print(f"⚠️ WAHA API responded with status code: {resp.status_code}")
except Exception as e:
    print(f"⚠️ WAHA API HTTP Check (http://localhost:3000) failed/offline: {e}")
    # Check DB settings fallback for waha_status
    try:
        cursor.execute("SELECT key, value FROM sunfra_system_settings WHERE key LIKE 'waha%'")
        rows = cursor.fetchall()
        print("  System Setting WAHA records:")
        for r in rows:
            print(f"    - {r[0]}: {r[1]}")
    except Exception:
        pass

# 3. Recent WAHA Events / Alerts in DB
print("\n--- 3. RECENT SYSTEM LOGS & EVENTS ---")
try:
    cursor.execute("SELECT id, event_type, status, details, timestamp FROM sunfra_waha_events ORDER BY id DESC LIMIT 5")
    events = cursor.fetchall()
    if events:
        print(f"Recent WAHA Events ({len(events)}):")
        for ev in events:
            print(f"  [{ev[4]}] Type: {ev[1]} | Status: {ev[2]} | Details: {ev[3]}")
    else:
        print("  No WAHA disconnect/error events logged.")
except Exception as e:
    print(f"  Could not read sunfra_waha_events: {e}")

# 4. Check Gmail / PAPAAK Connection Credentials
print("\n--- 4. PAPAAK GMAIL CONNECTION CHECK ---")
try:
    import imaplib
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login("kusum@sunfra.com", "kfgykqtorkchfkke")
    mail.select("inbox")
    status, data = mail.search(None, 'ALL')
    total_emails = len(data[0].split())
    print(f"✓ Gmail (kusum@sunfra.com) IMAP Login Successful (Total Inbox Emails: {total_emails})")
    mail.logout()
except Exception as e:
    print(f"❌ Gmail IMAP Connection Error: {e}")

# 5. Check Active Unified Reminders Status
print("\n--- 5. UNIFIED REMINDERS STATUS ---")
try:
    cursor.execute("SELECT status, count(*) FROM sunfra_unified_reminders GROUP BY status")
    rows = cursor.fetchall()
    for r in rows:
        print(f"  • Status '{r[0]}': {r[1]} reminders")
except Exception as e:
    print(f"  Error reading unified reminders: {e}")

print("\n==================================================================")
