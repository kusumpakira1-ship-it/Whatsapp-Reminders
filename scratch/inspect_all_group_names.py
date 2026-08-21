"""
List all unique group names in sunfra_raw_messages on 14 Aug 2026.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import RawMessage

db = SessionLocal()

target_date = datetime.date(2026, 8, 14)
start_of_day = datetime.datetime.combine(target_date, datetime.time.min)
end_of_day = datetime.datetime.combine(target_date, datetime.time.max)

msgs = db.query(RawMessage).filter(
    RawMessage.timestamp >= start_of_day,
    RawMessage.timestamp <= end_of_day
).all()

groups = {}
for m in msgs:
    g = m.group_name or 'DM / Unknown'
    groups[g] = groups.get(g, 0) + 1

print(f"=== UNIQUE GROUP NAMES ON 14 AUG 2026 ({len(groups)}) ===")
for g, count in sorted(groups.items(), key=lambda x: x[1], reverse=True):
    print(f"  {g:<45}: {count} msgs")

db.close()

