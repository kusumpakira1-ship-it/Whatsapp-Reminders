"""
Update sub_reports_status in Hostinger MySQL with %s placeholder
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import pymysql
import json

try:
    conn = pymysql.connect(
        host='145.223.17.70',
        user='u632391467_kusumpakira',
        password='Kusum@2026Bb!',
        database='u632391467_kusumpakira',
        connect_timeout=10
    )
    cursor = conn.cursor()
    
    # ID 295 (Sunfra Corporate P&L): All 6 reports submitted yesterday
    status_295 = json.dumps({
        "Day book": "done",
        "Daily sales": "done",
        "Daily purchases": "done",
        "Total Payables": "done",
        "Total Receivables": "done",
        "Each Sales P&L": "done"
    })
    cursor.execute("UPDATE sunfra_unified_reminders SET sub_reports_status = %s, status = 'sent' WHERE id = 295", (status_295,))
    
    # ID 185 (Accounts Poultry): All 8 reports submitted yesterday
    status_185 = json.dumps({
        "CA Statement": "done",
        "Day book": "done",
        "Daily sales": "done",
        "Daily purchases": "done",
        "Total Payables": "done",
        "Total Receivables": "done",
        "Average P&L": "done",
        "Each Sales P&L": "done"
    })
    cursor.execute("UPDATE sunfra_unified_reminders SET sub_reports_status = %s, status = 'sent' WHERE id = 185", (status_185,))

    # ID 269 (Summary - Sunfra Feeds): Update day book, daily sales, daily purchases, total payables, total receivables, each sales p&l
    status_269 = json.dumps({
        "Day book": "done",
        "Daily sales": "done",
        "Daily purchases": "done",
        "Total Payables": "done",
        "Total Receivables": "done",
        "Each Sales P&L": "done"
    })
    cursor.execute("UPDATE sunfra_unified_reminders SET sub_reports_status = %s WHERE id = 269", (status_269,))

    conn.commit()
    print("Successfully updated sub_reports_status in Hostinger MySQL!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
