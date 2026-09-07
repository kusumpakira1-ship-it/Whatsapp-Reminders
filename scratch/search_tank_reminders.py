import sqlite3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

print("=== 1. SEARCHING SQLITE DATABASE (whatsapp_reminders.sqlite) ===")
conn = sqlite3.connect('whatsapp_reminders.sqlite')
conn.row_factory = sqlite3.Row
c = conn.cursor()

tables = ['sunfra_unified_reminders', 'sunfra_tasks', 'sunfra_custom_alarms', 'sunfra_reminder_logs']
for t in tables:
    try:
        c.execute(f"SELECT * FROM {t}")
        rows = c.fetchall()
        print(f"\nTable '{t}' (total {len(rows)} rows):")
        for r in rows:
            row_str = str(dict(r)).lower()
            if 'tank' in row_str or 'water' in row_str:
                print("  MATCHING ROW:", dict(r))
            else:
                print("  Row:", dict(r).get('id'), "| Name/Notes:", dict(r).get('person_name') or dict(r).get('task_name'), "| Time:", dict(r).get('trigger_time') or dict(r).get('due_time'))
    except Exception as e:
        print(f"Error checking {t}: {e}")

print("\n=== 2. SEARCHING MYSQL DATABASE ===")
try:
    from database import SessionLocal
    from models import UnifiedReminder, Task, CustomAlarm
    db = SessionLocal()
    
    reminders = db.query(UnifiedReminder).all()
    print(f"\nMySQL UnifiedReminders count: {len(reminders)}")
    for r in reminders:
        r_str = f"{r.id} {r.person_name} {r.report_types} {r.task_notes}".lower()
        if 'tank' in r_str or 'water' in r_str:
            print("  MATCHING UNIFIED REMINDER:", r.id, r.person_name, r.report_types, r.task_notes, r.trigger_time)
            
    tasks = db.query(Task).all()
    print(f"\nMySQL Tasks count: {len(tasks)}")
    for t in tasks:
        t_str = f"{t.id} {t.task_name} {t.completion_details}".lower()
        if 'tank' in t_str or 'water' in t_str:
            print("  MATCHING TASK:", t.id, t.task_name, t.due_time)
            
    alarms = db.query(CustomAlarm).all()
    print(f"\nMySQL CustomAlarms count: {len(alarms)}")
    for a in alarms:
        a_str = str(a.__dict__).lower()
        if 'tank' in a_str or 'water' in a_str:
            print("  MATCHING ALARM:", a.id, a.__dict__)

except Exception as e:
    print("MySQL error:", e)

print("\n=== 3. SEARCHING PYTHON CODE FILES IN BACKEND ===")
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
for root, dirs, files in os.walk(backend_dir):
    for f in files:
        if f.endswith('.py'):
            fpath = os.path.join(root, f)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as file_obj:
                    content = file_obj.read()
                    if 'tank' in content.lower():
                        print(f"  FOUND 'tank' in file: {fpath}")
                        lines = content.split('\n')
                        for idx, l in enumerate(lines):
                            if 'tank' in l.lower():
                                print(f"    Line {idx+1}: {l.strip()}")
            except Exception as ex:
                pass
