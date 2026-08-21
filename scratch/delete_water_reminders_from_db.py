"""
Delete all Water Monitoring System rows from sunfra_unified_reminders
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import SessionLocal
from models import UnifiedReminder
from sqlalchemy import or_

db = SessionLocal()
try:
    water_rows = db.query(UnifiedReminder).filter(
        or_(
            UnifiedReminder.person_name.ilike('%water%'),
            UnifiedReminder.report_types.ilike('%water%')
        )
    ).all()
    count = len(water_rows)
    print(f"Found {count} Water Monitoring System rows in sunfra_unified_reminders.")
    for r in water_rows:
        db.delete(r)
    db.commit()
    print(f"Successfully deleted {count} Water Monitoring System rows from database!")
finally:
    db.close()
