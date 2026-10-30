import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from models import UnifiedReminder
from scheduler import clean_reminder_body

db = get_db_session()
r = db.query(UnifiedReminder).filter(UnifiedReminder.id == 979).first()

person_display = r.person_name if r.person_name and r.person_name.lower() not in ['team', 'team members', 'all', 'none'] else None

body_text = clean_reminder_body(r.task_notes)

greeting = f"Hi *{person_display}*,\n\n" if person_display else "Hi Team,\n\n"
msg = f"⏰ *Reminder*\n\n{greeting}{body_text}\n\nThank you! 🌱"

out_str = f"=== EXACT PREVIEW OF 11:00 PM MESSAGE FOR BALAJI ===\n{msg}\n====================================================\nTarget WhatsApp Group: {r.whatsapp_group_id}\nScheduled Trigger Time: {r.trigger_time}\nStatus: {r.status}\nFrequency: {r.frequency}\n"
with open("scratch/preview_balaji_msg.txt", "w", encoding="utf-8") as f:
    f.write(out_str)
print("Preview written successfully to scratch/preview_balaji_msg.txt")

db.close()
