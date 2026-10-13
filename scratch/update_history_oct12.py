import sys, os, json
sys.path.insert(0, os.path.abspath('backend'))
from database import get_db_session
from sqlalchemy import text

db = get_db_session()
val = db.execute(text("SELECT `value` FROM sunfra_system_settings WHERE `key` = 'daily_company_failure_history'")).scalar()
if val:
    hist = json.loads(val)
    hist.setdefault('balaji', {})['12 Oct 2026'] = 1
    hist.setdefault('corporate', {})['12 Oct 2026'] = 7
    hist.setdefault('feeds', {})['12 Oct 2026'] = 3
    hist.setdefault('farms', {})['12 Oct 2026'] = 4
    updated_str = json.dumps(hist)
    db.execute(text("UPDATE sunfra_system_settings SET `value` = :val WHERE `key` = 'daily_company_failure_history'"), {'val': updated_str})
    db.commit()
    print("Successfully updated daily_company_failure_history for 12 Oct 2026:")
    print("  • balaji: 1\n  • corporate: 7\n  • feeds: 3\n  • farms: 4")
db.close()
