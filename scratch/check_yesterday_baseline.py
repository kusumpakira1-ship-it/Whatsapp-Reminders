import sys, os, json
from datetime import datetime, date, timedelta
import pytz

sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import get_db_session
from sqlalchemy import text
from scheduler import build_7_company_escalation_reports

IST = pytz.timezone('Asia/Kolkata')
db = get_db_session()

print("=== 1. DAILY COMPANY FAILURE HISTORY FROM DB SETTINGS ===")
try:
    val = db.execute(text("SELECT `value` FROM sunfra_system_settings WHERE `key` = 'daily_company_failure_history'")).scalar()
    if val:
        hist = json.loads(val)
        print("Failure history for 12 Oct 2026:")
        for comp, d_map in hist.items():
            print(f"  • {comp}: {d_map.get('12 Oct 2026', 'N/A')} failed")
except Exception as e:
    print("Error reading failure history:", e)

print("\n=== 2. RUNNING BUILD_7_COMPANY_ESCALATION_REPORTS FOR YESTERDAY (12 Oct 2026) ===")
yesterday_dt = datetime(2026, 10, 12, 23, 50, 0)
try:
    res = build_7_company_escalation_reports(db, yesterday_dt)
    msgs_1159 = res[1]
    print(f"Generated {len(msgs_1159)} company escalation messages for 12 Oct 2026:\n")
    for idx, msg in enumerate(msgs_1159, 1):
        print(f"--- Company {idx} Message ---")
        print(msg)
        print()
except Exception as e:
    print("Error generating escalation report for yesterday:", e)

db.close()
