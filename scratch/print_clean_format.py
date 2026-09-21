import sys
import sqlite3
from datetime import date

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('backend/whatsapp_reminders.sqlite')
cur = conn.cursor()

today = str(date.today())

cur.execute('''
    SELECT company_name, employee_name, login_time, logout_time, status_badge 
    FROM sunfra_attendance_logs 
    WHERE date = ? 
    ORDER BY company_name, employee_name
''', (today,))

rows = cur.fetchall()

# Deduplicate by (company_name, employee_name) taking non-absent status if available
unique_dict = {}
for r in rows:
    c_name, e_name, l_in, l_out, st_badge = r
    key = (c_name, e_name)
    if key not in unique_dict or ("Absent" in unique_dict[key][4] and "Absent" not in st_badge):
        unique_dict[key] = r

unique_rows = list(unique_dict.values())
unique_rows.sort(key=lambda x: (x[0], x[1]))

tot_employees = len(unique_rows)
tot_present = sum(1 for r in unique_rows if "🟢 Present" in r[4])
tot_half_day = sum(1 for r in unique_rows if "🟡 Half Day" in r[4])
tot_leave = sum(1 for r in unique_rows if "🔵 On Leave" in r[4])
tot_absent = sum(1 for r in unique_rows if "🔴 Absent" in r[4])

msg = []
msg.append("📋 *Daily Attendance Report*")
msg.append("📅 *Date:* 16 Sep 2026")
msg.append("==================================================")

current_comp = None
for r in unique_rows:
    c_name, e_name, l_in, l_out, st_badge = r
    if c_name != current_comp:
        current_comp = c_name
        msg.append(f"\n🏢 *{c_name}*")
    msg.append(f"  • *{e_name}*: {st_badge}")

msg.append("\n==================================================")
msg.append("📊 *OVERALL STATS:*")
msg.append(f"👥 Total Employees: *{tot_employees}*")
msg.append(f"🟢 Present (Full Day): *{tot_present}*")
msg.append(f"🟡 Half Day: *{tot_half_day}*")
msg.append(f"🔵 On Leave: *{tot_leave}*")
msg.append(f"🔴 Absent: *{tot_absent}*")
msg.append("==================================================")

final_text = "\n".join(msg)
print(final_text)
