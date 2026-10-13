import sys, os
from datetime import datetime
import pytz

sys.path.insert(0, os.path.abspath('backend'))
from database import get_db_session
from sqlalchemy import text

IST = pytz.timezone('Asia/Kolkata')
now = datetime.now(IST)
today_date = now.strftime('%Y-%m-%d')
today_weekday = now.strftime('%A')

print(f"Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')} IST ({today_weekday})")
print("="*60)

db = get_db_session()

print("\n--- 1. REPORT RECIPIENTS (sunfra_report_recipients) ---")
try:
    recipients = db.execute(text("SELECT id, name, phone_number, is_active FROM sunfra_report_recipients")).fetchall()
    for r in recipients:
        print(f"  ID {r[0]}: {r[1]} | Phone: {r[2]} | Active: {r[3]}")
    if not recipients:
        print("  None found.")
except Exception as e:
    print(f"  Error: {e}")

print("\n--- 2. SYSTEM SETTINGS (sunfra_system_settings) ---")
try:
    settings = db.execute(text("SELECT `key`, `value` FROM sunfra_system_settings")).fetchall()
    for s in settings:
        print(f"  {s[0]}: {s[1]}")
    if not settings:
        print("  None found.")
except Exception as e:
    print(f"  Error: {e}")

print("\n--- 3. UNIFIED REMINDERS / SCHEDULED REPORTS IN DB ---")
try:
    rems = db.execute(text("""
        SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status 
        FROM sunfra_unified_reminders 
        ORDER BY TIME(trigger_time) ASC
    """)).fetchall()
    print(f"Total Unified Reminders: {len(rems)}")
    for r in rems:
        print(f"  [ID {r[0]}] {r[1]} ({r[2]}) | Time: {r[6]} | Freq: {r[7]} | Status: {r[8]} | Reports: {r[4]} | Notes: {r[5]}")
except Exception as e:
    print(f"  Error: {e}")

print("\n--- 4. TASKS DUE TODAY (sunfra_tasks) ---")
try:
    tasks = db.execute(text("""
        SELECT id, task_name, assignee_name, whatsapp_group_id, due_time, frequency, status 
        FROM sunfra_tasks 
        ORDER BY TIME(due_time) ASC
    """)).fetchall()
    print(f"Total Tasks: {len(tasks)}")
    for t in tasks:
        print(f"  [ID {t[0]}] Due: {t[4]} | Task: {t[1]} | Assignee: {t[2]} | Freq: {t[5]} | Status: {t[6]}")
except Exception as e:
    print(f"  Error: {e}")

print("\n--- 5. CUSTOM ALARMS (sunfra_custom_alarms) ---")
try:
    alarms = db.execute(text("""
        SELECT id, title, target_phone, alarm_time, status, is_recurring 
        FROM sunfra_custom_alarms 
        ORDER BY alarm_time ASC
    """)).fetchall()
    print(f"Total Alarms: {len(alarms)}")
    for a in alarms:
        print(f"  [ID {a[0]}] Time: {a[3]} | Title: {a[1]} | Phone: {a[2]} | Recur: {a[5]} | Status: {a[4]}")
except Exception as e:
    print(f"  Error: {e}")

db.close()
