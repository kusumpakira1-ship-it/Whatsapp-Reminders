import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')

from database import SessionLocal
from models import CustomAlarm, Task, UnifiedReminder
from datetime import datetime, date, timedelta

db = SessionLocal()

# Locations List
locations = [
    "Shead 1",
    "Shead 2",
    "Shead 3",
    "Shead 4",
    "Shead 5",
    "Shead 6",
    "Shead 7",
    "Shead 8",
    "Chick Shead",
    "Grower Shead",
    "Egg Godown",
    "Feed Plant",
    "Office Space",
    "Staff Quarters" # Every 15 days / rotated
]

target_phone = "918247256522@c.us"
target_group = "120363409816800438@g.us"
person_name = "Nabiya"

# Starting Tomorrow (25 Aug 2026) at 9:00 AM
start_date = date(2026, 8, 25)

print("=== Creating Nabiya Daily Cleanliness Task Reminders in Database ===")

created_alarms = 0
for i, loc in enumerate(locations):
    # Calculate date for each location in sequence
    task_date = start_date + timedelta(days=i)
    trigger_dt = datetime(task_date.year, task_date.month, task_date.day, 9, 0, 0)

    msg_text = f"🔔 *Daily Surrounding & Cleanliness Task Reminder*\n\nHi {person_name},\n\nPlease complete today’s *Surrounding & Cleanliness task* by the end of the day for *{loc}*. Kindly send a video showing the surrounding and cleanliness status once the task is completed.\n\nThank you..."

    # 1. Insert into Custom Alarms
    alarm = CustomAlarm(
        target_type="group",
        whatsapp_target_id=target_group,
        report_type=f"Cleanliness Task - {loc}",
        frequency="once" if loc == "Staff Quarters" else "daily",
        repeat_interval="none",
        task_notes=msg_text,
        trigger_time=trigger_dt,
        status="pending"
    )
    db.add(alarm)
    
    # 2. Insert into Unified Reminders for Task & Approvals Dashboard
    unif = UnifiedReminder(
        person_name=person_name,
        whatsapp_group_id=target_group,
        report_types=f"Cleanliness Task: {loc}",
        trigger_time=trigger_dt,
        frequency="daily",
        status="pending"
    )
    db.add(unif)
    created_alarms += 1
    print(f"Scheduled Day {i+1} ({task_date.strftime('%d %b %Y')} 09:00 AM): Location = {loc}")

db.commit()
db.close()
print(f"\nSuccessfully created {created_alarms} task schedule entries starting TOMORROW at 9:00 AM!")
