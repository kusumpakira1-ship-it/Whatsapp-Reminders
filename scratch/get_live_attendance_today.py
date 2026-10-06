import sys
import os
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message
from database import get_db_session
from sqlalchemy import text

db = get_db_session()
try:
    res = db.execute(text("SELECT MAX(timestamp) FROM sunfra_raw_messages")).fetchone()
    max_raw = res[0] if res else None
    res2 = db.execute(text("SELECT MAX(timestamp) FROM sunfra_whatsapp_messages")).fetchone()
    max_wa = res2[0] if res2 else None
    print(f"Max raw msg timestamp in DB: {max_raw}")
    print(f"Max WA msg timestamp in DB: {max_wa}")
finally:
    db.close()

today_str = date.today().strftime('%Y-%m-%d')
print(f"\nGenerating Live Attendance Report for date: {today_str}...")

data = evaluate_attendance_for_date(today_str)
msg = generate_attendance_summary_message(data)

print("\n" + msg)
