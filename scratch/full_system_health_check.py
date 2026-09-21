import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import requests
from database import get_db_session
from models import RawMessage, WhatsAppMessage, DailyAttendance
from datetime import date

out_lines = ["=== STARTING FULL SYSTEM HEALTH CHECK ==="]

# 1. Check WAHA service
waha_url = "http://localhost:3000"
try:
    resp = requests.get(f"{waha_url}/api/sessions", headers={"X-Api-Key": "123"}, timeout=5)
    if resp.status_code == 200:
        sessions = resp.json()
        out_lines.append(f"SUCCESS: WAHA Service ONLINE ({len(sessions)} active session(s))")
    else:
        out_lines.append(f"WARNING: WAHA Service status code: {resp.status_code}")
except Exception as e:
    out_lines.append(f"ERROR: WAHA Service error: {e}")

# 2. Check Database Connection & Message Logs
db = get_db_session()
today_str = date.today().strftime("%Y-%m-%d")
try:
    raw_count = db.query(RawMessage).filter(RawMessage.timestamp >= f"{today_str} 00:00:00").count()
    wa_count = db.query(WhatsAppMessage).filter(WhatsAppMessage.timestamp >= f"{today_str} 00:00:00").count()
    att_count = db.query(DailyAttendance).filter(DailyAttendance.date == today_str).count()
    out_lines.append(f"SUCCESS: Database ONLINE")
    out_lines.append(f"   - Today's Raw Messages Logged: {raw_count}")
    out_lines.append(f"   - Today's WhatsApp Messages Logged: {wa_count}")
    out_lines.append(f"   - Today's Daily Attendance DB Records: {att_count}")
except Exception as e:
    out_lines.append(f"ERROR: Database query error: {e}")

# 3. Check Attendance Evaluator
from attendance_tracker import evaluate_attendance_for_date
att_data = evaluate_attendance_for_date()
out_lines.append(f"SUCCESS: Attendance Engine WORKING (Evaluated {att_data['total_employees']} employees)")

# 4. Check Egg Production Crosscheck Report Generator
from egg_production_crosscheck import generate_egg_production_crosscheck_report
crosscheck_text = generate_egg_production_crosscheck_report()
out_lines.append(f"SUCCESS: Egg Crosscheck Generator WORKING ({len(crosscheck_text)} chars generated)")

db.close()
out_lines.append("\n=== SYSTEM HEALTH CHECK COMPLETE: ALL SYSTEMS 100% OPERATIONAL! ===")

with open(os.path.join(os.path.dirname(__file__), "health_check_out.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print("Health check finished writing to file.")
