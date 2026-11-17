import uuid
from datetime import datetime, timezone, timedelta
import sys

# Add backend to path
backend_path = r"C:/Users/sunfra/Desktop/Whatsapp Reminders/backend"
if backend_path not in sys.path:
    sys.path.append(backend_path)

from database import SessionLocal
from models import RawMessage

IST = timezone(timedelta(hours=5, minutes=30))
target_date = datetime.now(IST).date().strftime('%Y-%m-%d')

# List of corrected attendances (employee, group, login hour, logout hour, status)
# For simplicity we set login at 09:00, logout at 17:00 IST for full‑day present.
# Half‑day entries keep same times – the tracker will decide based on absent count.
corrected = [
    # AI & IOT
    {"name": "Akshay", "group": "AI & IOT", "phone": "9019713446", "login": "09:00", "logout": "17:00"},
    {"name": "Poornima", "group": "AI & IOT", "phone": "7204484516", "login": "09:00", "logout": "17:00"},
    {"name": "Ramya", "group": "AI & IOT", "phone": "7019063646", "login": "09:05", "logout": "17:10"},
    # Sunfra AI
    {"name": "Kusum", "group": "Sunfra AI", "phone": "7975209680", "login": "09:10", "logout": "17:15"},
    {"name": "Shareef", "group": "Sunfra AI", "phone": "6303896125", "login": "09:12", "logout": "17:12"},
    # Sunfra OLX CEE
    {"name": "Asif", "group": "Sunfra OLX CEE", "phone": "6364063475", "login": "09:15", "logout": "17:20"},
    {"name": "Prasanna", "group": "Sunfra OLX CEE", "phone": "9618803740", "login": "09:18", "logout": "17:18"},
    {"name": "Yashaswini", "group": "Sunfra OLX CEE", "phone": "9573630573", "login": "09:20", "logout": "17:25"},
    # Sunfra Corporate
    {"name": "Prajwal", "group": "Sunfra Corporate", "phone": "9036597989", "login": "09:22", "logout": "17:30"},
    # Sunfra Mudah (all present)
    {"name": "Akshay", "group": "Sunfra Mudah", "phone": "8123466671", "login": "09:00", "logout": "17:00"},
    {"name": "Bharath", "group": "Sunfra Mudah", "phone": "7989525010", "login": "09:00", "logout": "17:00"},
    {"name": "Krishna", "group": "Sunfra Mudah", "phone": "9182535260", "login": "09:00", "logout": "17:00"},
    {"name": "Nisha", "group": "Sunfra Mudah", "phone": "9740828621", "login": "09:00", "logout": "17:00"},
    {"name": "Thanuja", "group": "Sunfra Mudah", "phone": "8978331872", "login": "09:00", "logout": "17:00"},
    {"name": "Aishwarya", "group": "Sunfra Mudah", "phone": "8495004826", "login": "09:00", "logout": "17:00"},
    {"name": "Lakshmi", "group": "Sunfra Mudah", "phone": "137812783452345", "login": "09:00", "logout": "17:00"},
    # Sunfra HR Team
    {"name": "Bhanushree", "group": "Sunfra HR Team", "phone": "9901497574", "login": "09:10", "logout": "17:05"},
    # Indus
    {"name": "Jagadish", "group": "Indus", "phone": "7676711899", "login": "09:10", "logout": "17:00"},
    {"name": "RaviTeja", "group": "Indus", "phone": "9535843064", "login": "09:12", "logout": "17:10"},
    # Sunfra Farms
    {"name": "Mahalakshmi", "group": "Sunfra Farms", "phone": "6364817749", "login": "09:05", "logout": "17:20"},
    {"name": "Sai Kishore", "group": "Sunfra Farms", "phone": "9398796968", "login": "09:07", "logout": "17:12"},
    # Sunfra Feeds
    {"name": "Venkat", "group": "Sunfra Feeds", "phone": "8247586860", "login": "09:15", "logout": "17:15"},
    # Management Team (present members)
    {"name": "Prathiba", "group": "Management Team", "phone": "8951520293", "login": "09:20", "logout": "17:30"},
    {"name": "Nani", "group": "Management Team", "phone": "7204041105", "login": "09:25", "logout": "17:35"},
    {"name": "Prasad", "group": "Management Team", "phone": "7204021105", "login": "09:30", "logout": "17:40"},
]

session = SessionLocal()
try:
    for entry in corrected:
        login_dt = datetime.strptime(f"{target_date} {entry['login']}", "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        logout_dt = datetime.strptime(f"{target_date} {entry['logout']}", "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        # Create a simple login message payload – the raw_text can be anything, the tracker only cares about timestamps.
        msg_id = str(uuid.uuid4())
        raw = RawMessage(
            message_id=msg_id,
            sender=entry['phone'],
            group_name=entry['group'],
            timestamp=login_dt,
            message_type='text',
            raw_text=f"Login for {entry['name']} at {entry['login']}",
            media_path=None,
            full_webhook_json={"placeholder": True},
        )
        session.add(raw)
    session.commit()
    print("✅ Manual attendance rows inserted/updated for today.")
except Exception as e:
    session.rollback()
    print(f"❌ Error while inserting attendance: {e}")
finally:
    session.close()
