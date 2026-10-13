import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append('backend')
from database import get_db_session
from models import PapaakEggRate
from datetime import date

db = get_db_session()
records = db.query(PapaakEggRate).filter(
    PapaakEggRate.category == "loading"
).all()

count = 0
for r in records:
    if r.raw_text and "VEH KOL" in r.raw_text:
        r.category = "paper"
        count += 1

db.commit()
print(f"Updated {count} records to category='paper'.")

from papaak_email_service import generate_daily_egg_rates_report
rep = generate_daily_egg_rates_report(target_date=date(2026, 10, 12), report_number=1)
print("\n--- REPORT OUTPUT ---")
print(rep)
db.close()
