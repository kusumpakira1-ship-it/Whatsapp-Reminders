import asyncio
from scheduler import scheduled_godown_report_job

if __name__ == "__main__":
    print("Testing 9 PM Egg Godown Report...")
    asyncio.run(scheduled_godown_report_job())
    print("Egg Godown Report tested.")
