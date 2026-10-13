import sys, os
from datetime import datetime, time
import pytz

sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import get_db_session
from sqlalchemy import text
from scheduler import setup_scheduler, scheduler

IST = pytz.timezone('Asia/Kolkata')
now = datetime.now(IST)
today_date = now.date()

print(f"Current Date/Time: {now.strftime('%Y-%m-%d %I:%M:%S %p')} IST ({now.strftime('%A')})\n")

try:
    setup_scheduler()
except Exception:
    pass

jobs = scheduler.get_jobs()

# Sort APScheduler jobs by today's fire time or next fire time
job_list = []
for job in jobs:
    trigger = job.trigger
    midnight_today = IST.localize(datetime.combine(today_date, time(0, 0, 0)))
    
    # Calculate fire times today
    curr = midnight_today
    fire_times_today = []
    for _ in range(1500):
        nxt = trigger.get_next_fire_time(None, curr)
        if nxt and nxt.date() == today_date:
            fire_times_today.append(nxt)
            curr = nxt
        else:
            break
            
    next_run = trigger.get_next_fire_time(None, now)
    job_list.append({
        'id': job.id,
        'name': job.name,
        'func': job.func.__name__ if hasattr(job.func, '__name__') else str(job.func),
        'trigger': str(trigger),
        'fire_today': fire_times_today,
        'next_run': next_run
    })

print("=== 1. APSCHEDULER JOBS SCHEDULED FOR TODAY ===")
today_only = [j for j in job_list if len(j['fire_today']) > 0 and len(j['fire_today']) <= 5] # non-high-frequency
today_only.sort(key=lambda x: x['fire_today'][0])

for j in today_only:
    times_str = ", ".join([t.strftime('%I:%M %p') for t in j['fire_today']])
    print(f"Time: {times_str:<22} | Job: {j['id']}")

print("\n=== 2. APSCHEDULER HIGH FREQUENCY (INTERVAL) JOBS ===")
high_freq = [j for j in job_list if len(j['fire_today']) > 5]
for j in high_freq:
    print(f"Trigger: {j['trigger']:<30} | Job: {j['id']}")

print("\n=== 3. APSCHEDULER WEEKLY / MONTHLY / FUTURE JOBS ===")
future_jobs = [j for j in job_list if len(j['fire_today']) == 0]
for j in future_jobs:
    next_str = j['next_run'].strftime('%Y-%m-%d %I:%M %p') if j['next_run'] else 'Never'
    print(f"Next Run: {next_str:<22} | Trigger: {j['trigger']:<40} | Job: {j['id']}")

print("\n=== 4. DATABASE UNIFIED REMINDERS / SCHEDULED INPUT REPORTS TODAY ===")
db = get_db_session()
try:
    rems = db.execute(text("""
        SELECT id, person_name, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, status 
        FROM sunfra_unified_reminders 
        ORDER BY TIME(trigger_time) ASC
    """)).fetchall()
    for r in rems:
        id_, name, grp, rep, notes, trig, freq, status = r
        t_str = trig.strftime('%I:%M %p') if trig else 'N/A'
        print(f"Time: {t_str:<10} | Freq: {freq:<8} | Status: {status:<8} | Person: {name:<12} | Reports: {rep}")
finally:
    db.close()
