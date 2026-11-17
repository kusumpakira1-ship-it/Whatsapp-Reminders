import sys, os
sys.path.insert(0, os.path.abspath('backend'))

from scheduler import setup_scheduler, scheduler

try:
    setup_scheduler()
except Exception:
    pass

print("=== CHECKING WEEKLY COMPREHENSIVE REPORT JOBS ===")
jobs = [j for j in scheduler.get_jobs() if 'weekly_comprehensive' in j.id]
for j in jobs:
    print(f"Job ID: {j.id:<45} | Trigger: {j.trigger}")

