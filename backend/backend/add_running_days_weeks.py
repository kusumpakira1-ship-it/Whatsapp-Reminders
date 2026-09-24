import sys, os
from datetime import datetime
sys.path.append('/app')

from database import engine, SessionLocal
from sqlalchemy import text, inspect
from models import Flock

# 1. Check and add columns to DB
with engine.connect() as conn:
    # Try adding running_days column
    try:
        conn.execute(text("ALTER TABLE sunfra_flocks ADD COLUMN running_days INT DEFAULT 0"))
        print("Added running_days column")
    except Exception as e:
        print("running_days column may already exist:", e)
        
    # Try adding running_weeks column
    try:
        conn.execute(text("ALTER TABLE sunfra_flocks ADD COLUMN running_weeks INT DEFAULT 0"))
        print("Added running_weeks column")
    except Exception as e:
        print("running_weeks column may already exist:", e)
    conn.commit()

# 2. Compute and update running_days & running_weeks for all active flocks
db = SessionLocal()
today = datetime.now().date()
flocks = db.query(Flock).all()

print("\n=== UPDATING SUNFRA_FLOCKS RUNNING DAYS & RUNNING WEEKS ===")
for f in flocks:
    if f.hatch_date:
        days = (today - f.hatch_date).days + 1
        weeks = days // 7
        f.running_days = max(0, days)
        f.running_weeks = max(0, weeks)
        print(f"Shed: {f.shed_name:<10} | Hatch: {f.hatch_date} | Running Days: {f.running_days:<4} | Running Weeks: {f.running_weeks:<3}")

db.commit()
db.close()
print("\nsunfra_flocks database table successfully updated!")
