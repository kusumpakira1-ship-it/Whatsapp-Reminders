import sys, uuid
from datetime import datetime, timezone, timedelta

backend_path = r"C:/Users/sunfra/Desktop/Whatsapp Reminders/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from database import SessionLocal
from models import RawMessage

IST = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(IST).date().strftime('%Y-%m-%d')

# Employees to correct: (name, phone, new_login_time)
corrections = [
    {"name": "Sai Kishore", "phone": "9398796968", "login": "11:50"},
    {"name": "Ramya", "phone": "7019063646", "login": "11:50"},
]

session = SessionLocal()
try:
    for entry in corrections:
        # Delete previous login messages for today
        deleted = session.query(RawMessage).filter(
            RawMessage.sender == entry["phone"],
            RawMessage.timestamp >= f"{today_str} 00:00:00",
            RawMessage.timestamp <= f"{today_str} 23:59:59",
            RawMessage.raw_text.like('Login for%')
        ).delete(synchronize_session=False)
        # Insert corrected login
        login_dt = datetime.strptime(f"{today_str} {entry['login']}", "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        msg_id = str(uuid.uuid4())
        raw = RawMessage(
            message_id=msg_id,
            sender=entry['phone'],
            group_name='Sunfra Farms' if entry['name']=='Sai Kishore' else 'AI & IOT',
            timestamp=login_dt,
            message_type='text',
            raw_text=f"Login for {entry['name']} at {entry['login']}",
            full_webhook_json={"placeholder": True},
        )
        session.add(raw)
    session.commit()
    print(f"✅ Updated attendance for {len(corrections)} employees (deleted {deleted} old rows).")
except Exception as e:
    session.rollback()
    print(f"❌ Error updating attendance: {e}")
finally:
    session.close()
