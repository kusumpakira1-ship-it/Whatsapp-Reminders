import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from scheduler import build_7_company_escalation_reports

IST = timezone(timedelta(hours=5, minutes=30))
now_ist = datetime.now(IST).replace(tzinfo=None)

db = get_db_session()
messages_930, messages_1159, combined_1159_text = build_7_company_escalation_reports(db, now_ist)
db.close()

with open("scratch/today_oct24_escalation.txt", "w", encoding="utf-8") as f:
    f.write("=== 9:30 PM PER-COMPANY ESCALATION MESSAGES (4 COMPANIES) ===\n\n")
    for idx, msg in enumerate(messages_930, 1):
        f.write(f"--- Company {idx} (9:30 PM) ---\n")
        f.write(msg + "\n\n")
        
    f.write("\n=== 11:59 PM EOD PER-COMPANY ESCALATION MESSAGES (4 COMPANIES) ===\n\n")
    for idx, msg in enumerate(messages_1159, 1):
        f.write(f"--- Company {idx} (EOD Summary) ---\n")
        f.write(msg + "\n\n")
        
    f.write("\n=== 11:59 PM COMBINED ESCALATION SUMMARY ===\n\n")
    f.write(combined_1159_text + "\n")

print("Generated today's (Oct 24) 4-company escalation reports successfully!")
