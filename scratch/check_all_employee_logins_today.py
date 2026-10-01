import sys
import sqlite3
import datetime

sys.path.append('backend')
from database import SessionLocal, get_db_session
from attendance_tracker import COMMUNITY_EMPLOYEES
from sqlalchemy import text

sys.stdout.reconfigure(encoding='utf-8')

today_str = datetime.datetime.now().strftime("%Y-%m-%d")
print(f"================ TODAY'S ({today_str}) LOGIN STATUS FOR ALL EMPLOYEES ================")

raws = []
try:
    db = get_db_session()
    query = text(f"""
        SELECT sender, group_name, raw_text, timestamp 
        FROM sunfra_raw_messages 
        WHERE DATE(timestamp) = '{today_str}'
        ORDER BY timestamp ASC
    """)
    raws = db.execute(query).fetchall()
    print(f"Fetched {len(raws)} total raw messages for today ({today_str}).\n")
    db.close()
except Exception as e:
    print("Database Query Error:", e)

# Keywords to detect login / attendance messages
login_keywords = [
    "login", "log in", "logged in", "loged in", "logedin", "logging in",
    "sign in", "signing in", "signed in", "morning team", "good morning",
    "morning", "present", "in", "im in", "i'm in", "hi", "hello", "started"
]

for grp_data in COMMUNITY_EMPLOYEES:
    grp_name = grp_data["group"]
    grp_jids_lower = [j.lower() for j in grp_data.get("group_jids", [])] + [grp_name.lower()]
    
    print(f"\n🏢 Group / Department: *{grp_name}*")
    
    for emp in grp_data["employees"]:
        emp_name = emp["name"]
        phone = emp["phone"]
        aliases = emp.get("aliases", [])
        
        matched_msgs = []
        for r in raws:
            s_str = str(r[0] or "").lower()
            g_str = str(r[1] or "").lower()
            text_str = str(r[2] or "").lower()
            
            is_sender = (phone in s_str) or (("91" + phone) in s_str) or any(al.lower() in s_str for al in aliases)
            
            if is_sender:
                matched_msgs.append(r)
                
        if matched_msgs:
            earliest_msg = matched_msgs[0]
            login_time_str = str(earliest_msg[3])
            clean_text = (earliest_msg[2] or "").replace('\n', ' ')
            print(f"  • {emp_name}: 🟢 Logged in at {login_time_str} | Text: \"{clean_text[:60]}\"")
        else:
            print(f"  • {emp_name}: 🔴 No Login / Message Recorded Today")
