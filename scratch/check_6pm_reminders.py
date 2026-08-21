"""
Check all reminders scheduled for 6:00 PM (18:00 IST) on 15 Aug 2026 and verify execution logs.
"""
import sys, os
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from database import SessionLocal
from sqlalchemy import text

print("--- CHECKING 6:00 PM IST REMINDERS STATUS ---")
today_str = "2026-08-15"

db = SessionLocal()
try:
    print(f"\n1. Unified Reminders Scheduled around 6:00 PM:")
    reminders = db.execute(text("SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, status, frequency FROM sunfra_unified_reminders")).fetchall()
    for r in reminders:
        dt_str = str(r[6])
        if '18:00' in dt_str or '06:00:00' in dt_str or '17:59' in dt_str or '18:01' in dt_str:
            print(f"  - ID {r[0]} | {r[1]} ({r[2]}) | Reports: {r[4]} | Group: {r[3]} | Trigger: {r[6]} | Status: {r[7]}")

    print(f"\n2. Reminder Logs Executed Today ({today_str}):")
    logs = db.execute(text(f"""
        SELECT id, reminder_id, person_name, person_phone, whatsapp_group_id, report_types, trigger_time, executed_at, status, details
        FROM sunfra_reminder_logs
        WHERE DATE(executed_at) = '{today_str}'
        ORDER BY executed_at DESC
    """)).fetchall()
    
    if not logs:
        print("  (No logs found for today yet)")
    for l in logs:
        print(f"  - Log ID {l[0]} | Rem ID: {l[1]} | {l[2]} ({l[3]}) | Executed: {l[7]} | Status: {l[8]} | Details: {l[9]}")

    print(f"\n3. Company Tasks Scheduled Today:")
    tasks = db.execute(text(f"""
        SELECT id, task_name, assigned_person_name, assigned_person_phone, due_time, status, completion_details
        FROM sunfra_tasks
        WHERE DATE(due_time) = '{today_str}'
        ORDER BY due_time DESC
    """)).fetchall()
    for t in tasks:
        print(f"  - Task ID {t[0]} | {t[1]} | Assigned: {t[2]} ({t[3]}) | Due: {t[4]} | Status: {t[5]} | Details: {t[6]}")

except Exception as e:
    print(f"Error querying DB: {e}")
finally:
    db.close()
