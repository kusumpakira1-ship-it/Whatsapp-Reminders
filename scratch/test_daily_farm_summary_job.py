"""
Test executing 9:30 PM Daily Farm Summary Report job.
"""
import sys, os, datetime
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from daily_farm_summary import generate_daily_farm_summary_report

report = generate_daily_farm_summary_report()
print("=== GENERATED 9:30 PM DAILY FARM SUMMARY REPORT ===")
print(report)

