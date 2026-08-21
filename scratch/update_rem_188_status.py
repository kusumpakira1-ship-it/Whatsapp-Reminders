"""
Update sub_reports_status for Reminder 188 in Hostinger MySQL.
"""
import pymysql, sys, json
sys.stdout.reconfigure(encoding='utf-8')

host = '145.223.17.70'
db   = 'u632391467_kusumpakira'
user = 'u632391467_kusumpakira'
pass_ = 'Kusum@2026Bb!'

conn = pymysql.connect(host=host, user=user, password=pass_, database=db, cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

# 1. Update Reminder 188 (Corporate P&L) sub_reports_status
status_dict = {
    "Day book": "done",
    "Daily sales": "done",
    "Daily purchases": "done",
    "Total Payables": "done",
    "Total Receivables": "done",
    "Each Sales P&L": "done"
}
json_str = json.dumps(status_dict)

cursor.execute("UPDATE sunfra_unified_reminders SET sub_reports_status = %s WHERE id = 188", (json_str,))
conn.commit()
print("Updated Reminder 188 sub_reports_status in Hostinger MySQL successfully!")

# Verify
cursor.execute("SELECT id, person_name, report_types, sub_reports_status FROM sunfra_unified_reminders WHERE id = 188")
row = cursor.fetchone()
print("Verified Row:", row)

