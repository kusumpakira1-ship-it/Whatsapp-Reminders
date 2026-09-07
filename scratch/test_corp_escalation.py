import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from datetime import datetime, timezone, timedelta
from scheduler import build_7_company_escalation_reports

IST = timezone(timedelta(hours=5, minutes=30))
sept3_dt = datetime(2026, 9, 3, 22, 0, 0, tzinfo=IST)

db = SessionLocal()
res = build_7_company_escalation_reports(db, sept3_dt)

print("Type of res:", type(res), "Len:", len(res))
for i, item in enumerate(res):
    print(f"\nItem {i} type: {type(item)}")
    if isinstance(item, list):
        for sub in item:
            print("  Sub item:", sub)
    else:
        print("  Item content:", str(item)[:300])
