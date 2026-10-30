import sys
import os
from datetime import datetime, timezone, timedelta
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from scheduler import build_7_company_escalation_reports

# Target date: Yesterday (28 Oct 2026)
target_dt = datetime(2026, 10, 28, 23, 59, 0)

db = get_db_session()
try:
    messages_930, messages_1159, combined_1159_text = build_7_company_escalation_reports(db, target_dt, persist_eod=False)
finally:
    db.close()

print("==================================================")
print("=== 9:30 PM ESCALATION REPORTS (28 OCT 2026) ===")
print("==================================================")
for idx, m in enumerate(messages_930, 1):
    print(f"\n--- [9:30 PM] Company {idx} ---\n{m}\n")

print("\n==================================================")
print("=== 11:59 PM EOD ESCALATION REPORTS (28 OCT 2026) ===")
print("==================================================")
for idx, m in enumerate(messages_1159, 1):
    print(f"\n--- [11:59 PM EOD] Company {idx} ---\n{m}\n")
