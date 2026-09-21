import sys
import time

sys.path.append('backend')
from database import SessionLocal
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("Testing direct MySQL connection via SessionLocal...")

for i in range(3):
    try:
        db = SessionLocal()
        res = db.execute(text("SELECT COUNT(*) FROM sunfra_raw_messages WHERE date(timestamp) = '2026-09-16';")).fetchone()
        print(f"Success! Total 16 Sep messages in MySQL: {res[0]}")
        db.close()
        break
    except Exception as e:
        print(f"Attempt {i+1} failed: {e}")
        time.sleep(2)
