import sys, os
from datetime import datetime, time
import pytz

sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')

# Silence root logger to avoid verbose APScheduler info messages
import logging
logging.getLogger('apscheduler').setLevel(logging.WARNING)

from scheduler import setup_scheduler, scheduler

IST = pytz.timezone('Asia/Kolkata')
now = datetime.now(IST)
today_date = now.date()

print(f"Current Date/Time: {now.strftime('%Y-%m-%d %H:%M:%S')} IST ({now.strftime('%A')})")
print("="*100)

try:
    setup_scheduler()
except Exception as e:
    print("setup_scheduler notice:", e)

jobs = scheduler.get_jobs()
print(f"Total APScheduler Jobs Loaded: {len(jobs)}\n")

today_jobs = []

for job in jobs:
    trigger = job.trigger
    midnight_today = IST.localize(datetime.combine(today_date, time(0, 0, 0)))
    
    # Calculate all fire times for today
    fire_times_today = []
    curr = midnight_today
    for _ in range(1500): # max safety bound
        nxt = trigger.get_next_fire_time(None, curr)
        if nxt and nxt.date() == today_date:
            fire_times_today.append(nxt)
            curr = nxt
        else:
            break
            
    runs_today = len(fire_times_today) > 0
    next_run_from_now = trigger.get_next_fire_time(None, now)
    
    today_jobs.append({
        'id': job.id,
        'name': job.name,
        'func': job.func.__name__ if hasattr(job.func, '__name__') else str(job.func),
        'trigger': str(trigger),
        'runs_today': runs_today,
        'today_runs_count': len(fire_times_today),
        'next_run_from_now': next_run_from_now.strftime('%Y-%m-%d %I:%M %p IST') if next_run_from_now else "None"
    })

print(f"{'JOB ID':<42} | {'TRIGGER':<36} | {'RUNS TODAY?':<12} | {'NEXT RUN FROM NOW'}")
print("-" * 120)
for j in sorted(today_jobs, key=lambda x: x['id']):
    print(f"{j['id']:<42} | {j['trigger']:<36} | {str(j['runs_today']):<12} | {j['next_run_from_now']}")

try:
    scheduler.shutdown(wait=False)
except Exception:
    pass

sys.stdout.flush()
os._exit(0)
