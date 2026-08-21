"""
Check and add sub_reports_status column to sunfra_unified_reminders and sunfra_tasks tables
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE sunfra_unified_reminders ADD COLUMN sub_reports_status TEXT NULL;"))
        conn.commit()
        print("Added sub_reports_status to sunfra_unified_reminders!")
    except Exception as e:
        print("sunfra_unified_reminders:", e)

    try:
        conn.execute(text("ALTER TABLE sunfra_tasks ADD COLUMN sub_reports_status TEXT NULL;"))
        conn.commit()
        print("Added sub_reports_status to sunfra_tasks!")
    except Exception as e:
        print("sunfra_tasks:", e)
