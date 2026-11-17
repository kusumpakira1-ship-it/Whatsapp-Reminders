import sys, os, uuid
from datetime import datetime, timezone, timedelta
backend_path = r"C:/Users/sunfra/Desktop/Whatsapp Reminders/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from database import get_db_session
from models import RawMessage

def main():
    db = get_db_session()
    try:
        ist = timezone(timedelta(hours=5, minutes=30))
        today = datetime.now(ist).date()
        ts = datetime.combine(today, datetime.strptime('10:15 AM', '%I:%M %p').time()).replace(tzinfo=ist)
        msg_id = f"manual-{uuid.uuid4()}"
        raw = RawMessage(
            message_id=msg_id,
            sender='8886973517',
            group_name='Sunfra AI',
            timestamp=ts,
            message_type='text',
            raw_text='Login for Shruthi at 10:15 AM',
            full_webhook_json={'placeholder': True}
        )
        db.add(raw)
        db.commit()
        print('Inserted Shruthi login at', ts.isoformat())
    finally:
        db.close()

if __name__ == '__main__':
    main()

