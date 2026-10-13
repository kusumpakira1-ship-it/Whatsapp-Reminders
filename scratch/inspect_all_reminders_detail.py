import sys, os
from datetime import datetime
import pytz

sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')
from database import get_db_session
from sqlalchemy import text

IST = pytz.timezone('Asia/Kolkata')
now = datetime.now(IST)
today_date = now.date()

db = get_db_session()

print("=== CHECKING ALL 35 UNIFIED REMINDERS IN DATABASE ===")
rems = db.execute(text("""
    SELECT id, person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status 
    FROM sunfra_unified_reminders 
    ORDER BY TIME(trigger_time) ASC
""")).fetchall()

for r in rems:
    id_, name, phone, grp, rep, notes, trig, freq, status = r
    trig_time_str = trig.strftime('%Y-%m-%d %H:%M:%S') if trig else 'None'
    trig_time_only = trig.strftime('%I:%M %p') if trig else 'None'
    
    # Check if due today
    due_today = False
    if status == 'active' or status == 'pending':
        if freq == 'daily':
            due_today = True
        elif trig and trig.date() == today_date:
            due_today = True
            
    print(f"[ID {id_}] Status: {status:<8} | Freq: {freq:<8} | Time: {trig_time_only:<8} (Full: {trig_time_str}) | Person: {name} | Group: {grp} | Report/Task: {rep}")

print("\n=== CHECKING IF ANY REMINDERS SENT TODAY ===")
today_str = today_date.strftime('%Y-%m-%d')
try:
    sent_today = db.execute(text(f"""
        SELECT * FROM sunfra_reminder_logs 
        WHERE DATE(sent_at) = '{today_str}'
        ORDER BY sent_at DESC
    """)).fetchall()
    print(f"Total reminder logs today ({today_str}): {len(sent_today)}")
    for s in sent_today[:10]:
        print(" ", dict(s._mapping))
except Exception as e:
    print("Error checking reminder logs:", e)

db.close()
