import sys, os
sys.path.insert(0, os.path.abspath('backend'))
from database import get_db_session
from sqlalchemy import text

db = get_db_session()
dispatches = db.execute(text("SELECT `key`, `value` FROM sunfra_system_settings WHERE `key` LIKE '%2026-10-13%'")).fetchall()
print(f"Dispatches recorded for today (2026-10-13): {len(dispatches)}")
for d in dispatches:
    print(" ", d[0], ":", d[1])
db.close()
