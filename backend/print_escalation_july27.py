import os
import sys
import asyncio
from datetime import datetime, date, timedelta, timezone

# Reconfigure stdout to use UTF-8 to prevent charmap/encoding errors on emojis
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
os.chdir(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')

from dotenv import load_dotenv
load_dotenv(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\.env')

# Let's read scheduler.py
with open('scheduler.py', 'r', encoding='utf-8') as f:
    code = f.read()

# We will modify the code dynamically to run for July 27, 2026.
# We'll capture and print final_msg instead of sending it.

# Let's intercept send_waha_message to print it
code = code.replace(
    "send_waha_message(phone, final_msg)",
    "print('\\n--- REPORT FOR:', phone, '---\\n' + final_msg + '\\n-----------------------\\n')"
)

# Replace now_ist assignment in manager_escalation_job
old_manager_start = """async def manager_escalation_job():
    logger.info("Starting 9:30 PM Manager Escalation Check...")

    from datetime import datetime, timezone, timedelta
    import re
    import difflib
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)"""

new_manager_start = """async def manager_escalation_job():
    logger.info("Starting 9:30 PM Manager Escalation Check...")

    from datetime import datetime, timezone, timedelta
    import re
    import difflib
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime(2026, 7, 27, 21, 30, 0)
    end_of_day = now_ist.replace(hour=23, minute=59, second=59, microsecond=999999)"""

code = code.replace(old_manager_start, new_manager_start)

# Replace now_ist assignment in company_wise_escalation_job
old_company_start = """async def company_wise_escalation_job():
    logger.info("Starting 11:59 PM Company-Wise Manager Escalation Check...")

    from datetime import datetime, timezone, timedelta
    import re
    import difflib
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).replace(tzinfo=None)"""

new_company_start = """async def company_wise_escalation_job():
    logger.info("Starting 11:59 PM Company-Wise Manager Escalation Check...")

    from datetime import datetime, timezone, timedelta
    import re
    import difflib
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime(2026, 7, 27, 23, 59, 0)
    end_of_day = now_ist.replace(hour=23, minute=59, second=59, microsecond=999999)"""

code = code.replace(old_company_start, new_company_start)

# Add upper bounds to raw_messages_today and msg_jids queries in scheduler.py
code = code.replace(
    "raw_messages_today = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day).all()",
    "raw_messages_today = db.query(RawMessage).filter(RawMessage.timestamp >= start_of_day, RawMessage.timestamp <= end_of_day).all()"
)
code = code.replace(
    "msg_jids = {w.message_id: w.group_id for w in db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= start_of_day).all()}",
    "msg_jids = {w.message_id: w.group_id for w in db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= start_of_day, WhatsAppMessage.timestamp <= end_of_day).all()}"
)

# Exec the modified code to define the functions
namespace = {}
exec(code, namespace)

async def main():
    print("=================== 9:30 PM DAILY ESCALATION REPORT (27 July 2026) ===================")
    await namespace['manager_escalation_job']()
    print("\n=================== 11:59 PM COMPANY-WISE ESCALATION REPORT (27 July 2026) ===================")
    await namespace['company_wise_escalation_job']()

if __name__ == '__main__':
    asyncio.run(main())
