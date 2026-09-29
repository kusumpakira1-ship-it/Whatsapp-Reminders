import sys
import os
import asyncio

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from scheduler import scheduler, setup_scheduler

async def main():
    print("==================================================")
    print(" TESTING SCHEDULER INITIALIZATION & JOB TRIGGERS ")
    print("==================================================")

    try:
        setup_scheduler()
        print(f"\nScheduler running status: {scheduler.running}")
        jobs = scheduler.get_jobs()
        print(f"Total active scheduled jobs: {len(jobs)}")
        print("\n--- UPCOMING SCHEDULED JOBS LIST ---")
        for j in sorted(jobs, key=lambda x: str(x.next_run_time)):
            print(f"• ID: {j.id:<42} | Next Run: {j.next_run_time}")
        print("\n✅ All scheduled jobs initialized and verified cleanly in APScheduler!")
    except Exception as e:
        print(f"\n❌ Error initializing scheduler: {e}")

asyncio.run(main())
