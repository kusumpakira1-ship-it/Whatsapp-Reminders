import asyncio
from scheduler import manager_escalation_job

if __name__ == "__main__":
    print("Testing Manager Escalation Job...")
    asyncio.run(manager_escalation_job())
    print("Manager Escalation Job completed.")
