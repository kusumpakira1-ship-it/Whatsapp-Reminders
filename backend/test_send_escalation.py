import sys, os, asyncio
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
from dotenv import load_dotenv
load_dotenv(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\.env')

from scheduler import manager_escalation_job, company_wise_escalation_job, ESCALATION_REPORT_PHONES

print("Sending to these numbers:")
for p in ESCALATION_REPORT_PHONES:
    print(f"  {p}")
print()

async def run():
    print("Sending Daily Escalation Report to all 3 numbers...")
    await manager_escalation_job()
    print("Done. Sending Company-Wise Escalation Report to all 3 numbers...")
    await company_wise_escalation_job()
    print("Both reports sent successfully!")

asyncio.run(run())
