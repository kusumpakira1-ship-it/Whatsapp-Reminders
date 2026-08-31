import sys, os
from scheduler import build_7_company_escalation_reports
from database import SessionLocal
from datetime import datetime, timezone, timedelta
import zoho_reconciliation as zr

IST = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(IST)

# Escalation reports
db = SessionLocal()
messages_930, _ = build_7_company_escalation_reports(db, now)
print('--- ESCALATION REPORTS ---')
for i, msg in enumerate(messages_930, 1):
    print(f'[{i}]')
    print(msg)
    print('---')
db.close()

# Zoho Farm report
captured = []
orig_send = zr.send_waha_message
zr.send_waha_message = lambda phone, text: captured.append(text) or True
zr.generate_and_send_zoho_reconciliation_report()
print('--- ZOHO FARM REPORT ---')
if captured:
    print(captured[-1])
else:
    print('No farm report generated')
zr.send_waha_message = orig_send

# Zoho Feeds report
captured = []
zr.send_waha_message = lambda phone, text: captured.append(text) or True
zr.generate_and_send_sunfra_feeds_reconciliation_report()
print('--- ZOHO FEEDS REPORT ---')
if captured:
    print(captured[-1])
else:
    print('No feeds report generated')
