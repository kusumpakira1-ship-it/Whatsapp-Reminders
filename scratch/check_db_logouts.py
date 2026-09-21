import sys
sys.path.insert(0, 'backend')
from database import sqlite_engine
from sqlalchemy import text
from attendance_tracker import COMMUNITY_EMPLOYEES, evaluate_attendance_for_date

with sqlite_engine.connect() as conn:
    rows = conn.execute(text("SELECT sender, group_name, raw_text, timestamp FROM sunfra_raw_messages WHERE timestamp >= '2026-09-17 00:00:00' ORDER BY timestamp ASC")).fetchall()

print(f"Total raw messages in SQLite for today: {len(rows)}\n")

data = evaluate_attendance_for_date('2026-09-17')

print("DETAILED LOGOUT / SIGN-OFF REPORT PER GROUP & EMPLOYEE FOR TODAY (17 SEP 2026):\n")
for grp in data['groups']:
    gname = grp['group_name']
    print(f"==================== 🏢 {gname} ====================")
    for emp in grp['employees']:
        ename = emp['name']
        phone = emp['phone']
        ltime = emp['login_time']
        otime = emp['logout_time']
        badge = emp['status_badge']
        detail = emp['detail']
        
        # Find all raw messages for this employee in this group
        emp_msgs = []
        for r in rows:
            s_str = str(r[0] or '').lower()
            g_str = str(r[1] or '').lower()
            if ename.lower() in s_str or phone in s_str:
                emp_msgs.append((r[3], r[2]))
        
        print(f"• {ename:<12} | Login: {ltime:<10} | Logout: {otime:<10} | Badge: {badge}")
        if emp_msgs:
            print("   Messages Sent:")
            for t, txt in emp_msgs:
                clean_txt = (txt or '').replace('\n', ' ')
                print(f"     [{t}] '{clean_txt}'")
        else:
            print("   Messages Sent: None")
        print("-" * 50)
