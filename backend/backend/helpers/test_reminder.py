import asyncio
import os
import sys

# Ensure app is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scheduler import scheduled_targeted_reminder_job

print("Manually triggering the 5:30 PM reminder job now...")
asyncio.run(scheduled_targeted_reminder_job())
print("Job executed.")
