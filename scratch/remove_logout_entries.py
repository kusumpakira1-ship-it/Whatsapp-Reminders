import sys
from datetime import datetime, timezone, timedelta

backend_path = r"C:/Users/sunfra/Desktop/Whatsapp Reminders/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from database import SessionLocal
from models import RawMessage

IST = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(IST).date().strftime('%Y-%m-%d')

session = SessionLocal()
try:
    # Delete logout messages inserted earlier (raw_text starts with 'Logout for') for today
    deleted = session.query(RawMessage).filter(
        RawMessage.raw_text.like('Logout for%'),
        RawMessage.timestamp >= f"{today_str} 00:00:00",
        RawMessage.timestamp <= f"{today_str} 23:59:59"
    ).delete(synchronize_session=False)
    session.commit()
    print(f"✅ Deleted {deleted} logout entries for {today_str}.")
except Exception as e:
    session.rollback()
    print(f"❌ Error during deletion: {e}")
finally:
    session.close()

