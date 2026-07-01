import asyncio
import os
import sys

# Ensure app is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from services.scheduler import scheduled_targeted_reminder_job

print("Manually triggering the 5:30 PM reminder job now...")
asyncio.run(scheduled_targeted_reminder_job())
print("Job executed.")
