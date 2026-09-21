import sys
import sqlite3
import time

sys.path.append('backend')
from database import SessionLocal, get_db_session
from attendance_tracker import COMMUNITY_EMPLOYEES
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

print("================ TODAY'S (17 SEP 2026) LOGIN TIMINGS FOR ALL EMPLOYEES ================")

raws = []
try:
    db = SessionLocal()
    query = text("""
        SELECT sender, group_name, raw_text, timestamp 
        FROM sunfra_raw_messages 
        WHERE timestamp >= '2026-09-17 00:00:00' AND timestamp <= '2026-09-17 23:59:59'
        ORDER BY timestamp ASC
    """)
    raws = db.execute(query).fetchall()
    print(f"Successfully fetched {len(raws)} raw messages from MySQL for today (17 Sep)!\n")
    db.close()
except Exception as e:
    print("MySQL Error:", e)
    # Check SQLite
    try:
        conn = sqlite3.connect("whatsapp_reminders.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT sender, group_name, raw_text, timestamp FROM sunfra_raw_messages WHERE timestamp >= '2026-09-17 00:00:00' ORDER BY timestamp ASC;")
        raws = cursor.fetchall()
        print(f"Fetched {len(raws)} raw messages from local SQLite fallback!\n")
        conn.close()
    except Exception as sqle:
        print("SQLite Error:", sqle)

# Print per group and employee
login_keywords = ["login", "log in", "logged in", "loged in", "logedin", "logging in", "sign in", "signing in", "signed in", "morning team", "good morning", "morning", "present", "in", "im in", "i'm in"]

for grp_data in COMMUNITY_EMPLOYEES:
    grp_name = grp_data["group"]
    grp_jids_lower = [j.lower() for j in grp_data.get("group_jids", [])] + [grp_name.lower()]
    
    print(f"\n🏢 *{grp_name}*")
    
    for emp in grp_data["employees"]:
        emp_name = emp["name"]
        phone = emp["phone"]
        aliases = emp.get("aliases", [])
        
        matched_msgs = []
        for r in raws:
            s_str = str(r[0] or "").lower()
            g_str = str(r[1] or "").lower()
            
            is_sender = (phone in s_str) or (("91" + phone) in s_str) or any(al.lower() in s_str for al in aliases)
            is_group = any(target in g_str for target in grp_jids_lower)
            
            if is_sender and is_group:
                matched_msgs.append(r)
                
        if matched_msgs:
            earliest_msg = matched_msgs[0]
            login_time_str = earliest_msg[3]
            clean_text = (earliest_msg[2] or "").replace('\n', ' ')
            print(f"  • *{emp_name}*: 🟢 Logged in at {login_time_str} (Msg: '{clean_text[:40]}')")
        else:
            print(f"  • *{emp_name}*: 🔴 No Login Message Yet")
