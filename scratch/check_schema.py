import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import get_db_session
from sqlalchemy import text

db = get_db_session()
res = db.execute(text("DESCRIBE sunfra_unified_reminders")).fetchall()
for col in res:
    print(col)
db.close()
