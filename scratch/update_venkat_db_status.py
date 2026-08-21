"""
Update Venkat's reminder (ID 269) sub_reports_status in MySQL.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# Get row 269
cursor.execute("SELECT * FROM sunfra_unified_reminders WHERE id = 269")
row = cursor.fetchone()
print("Current row 269:", row)

new_sub_status = {
    "Day book": "done",
    "Daily sales": "done",
    "Daily purchases": "done",
    "Total Payables": "done",
    "Total Receivables": "done",
    "Each Sales P&L": "done"
}

cursor.execute("UPDATE sunfra_unified_reminders SET sub_reports_status = %s WHERE id = 269", (json.dumps(new_sub_status),))
conn.commit()
print("✅ Updated row 269 sub_reports_status to all done!")

conn.close()

