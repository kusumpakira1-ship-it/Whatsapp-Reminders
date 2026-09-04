import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from database import get_db, SessionLocal
from models import UnifiedReminder

print("=== TESTING GET_DB FALLBACK PROTECTION ===")

try:
    for db in get_db():
        rem_count = db.query(UnifiedReminder).count()
        print(f"✅ DB Session active! Total reminders found: {rem_count}")
        break
except Exception as e:
    print(f"❌ Error in get_db(): {e}")
