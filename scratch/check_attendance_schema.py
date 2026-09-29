import sqlite3
conn = sqlite3.connect('whatsapp_reminders.sqlite')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info('sunfra_attendance_logs')")
print('attendance_logs cols:', cursor.fetchall())
cursor.execute("PRAGMA table_info('sunfra_employees')")
print('employees cols:', cursor.fetchall())
