import sqlite3
from datetime import date

conn = sqlite3.connect('backend/whatsapp_reminders.sqlite')
cur = conn.cursor()

today = str(date.today())

records = [
    # (company, name, login, lunch_out, lunch_in, logout, status_type, status_badge)
    ("AI & IOT", "Akshay", None, None, None, None, "on_leave", "🔵 On Leave"),
    ("AI & IOT", "Kusum", "10:57 AM", "01:35 PM", "01:50 PM", None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("AI & IOT", "Poornima", "10:18 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("AI & IOT", "Ramya", "10:47 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Indus", "Girija", None, None, None, None, "absent", "🔴 Absent"),
    ("Indus", "Jagadish", None, None, None, None, "absent", "🔴 Absent"),
    ("Jataayu", "Roopa", "11:00 AM", None, None, "05:04 PM", "half_day_short", "🟡 Half Day (Short Hours < 8 Hrs)"),
    ("Management Team", "Balaji", "11:00 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Management Team", "Nani", "08:24 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Management Team", "Nikhil", None, None, None, None, "absent", "🔴 Absent"),
    ("Management Team", "Prasad", None, None, None, None, "absent", "🔴 Absent"),
    ("Management Team", "Prathiba", "09:31 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Management Team", "Vamsi", None, None, None, None, "absent", "🔴 Absent"),
    ("Sunfra Corporate", "Divya", "09:28 AM", "02:24 PM", "03:20 PM", None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra Corporate", "Prajwal", None, None, None, None, "absent", "🔴 Absent"),
    ("Sunfra Farms", "Mahalakshmi", "10:35 AM", "02:29 PM", "02:56 PM", None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra Feeds", "Venkat", None, None, None, None, "absent", "🔴 Absent"),
    ("Sunfra HR Team", "Bhanushree", "09:59 AM", "01:30 PM", None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra HR Team", "Parvati", "10:11 AM", "01:33 PM", "01:57 PM", None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra Mudah", "Aishwarya", None, None, None, None, "on_leave", "🔵 On Leave"),
    ("Sunfra Mudah", "Akshay", "07:41 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra Mudah", "Bharath", "08:12 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra Mudah", "Krishna", "08:15 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra Mudah", "Nisha", "08:12 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra Mudah", "Ravi Teja", "07:53 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra Mudah", "Thanuja", "09:40 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra OLX CEE", "Asif", "10:09 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra OLX CEE", "Prasanna", "10:54 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Sunfra OLX CEE", "Yashaswini", "10:31 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)"),
    ("Tendered", "Ganga", "10:27 AM", None, None, None, "half_day_no_logout", "🟡 Half Day (No Logout)")
]

for r in records:
    c_name, e_name, l_in, lu_out, lu_in, l_out, st_type, st_badge = r
    cur.execute('''
        INSERT OR REPLACE INTO sunfra_attendance_logs 
        (date, employee_name, company_name, login_time, lunch_start_time, lunch_end_time, logout_time, status_type, status_badge)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (today, e_name, c_name, l_in, lu_out, lu_in, l_out, st_type, st_badge))

conn.commit()
conn.close()
print("Successfully synced SQLite attendance logs!")
