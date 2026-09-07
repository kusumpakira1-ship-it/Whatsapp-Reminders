from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(IST)
print("Current Time IST:", now.strftime("%Y-%m-%d %H:%M:%S (%A)"))

schedules_today = [
    ("6:50 PM (18:50 IST)", "4 Consolidated Company Zoho Reconciliation Reports", "Sent to Kusum (7259510983) covering Farms, Feeds, Corporate, Indus"),
    ("9:00 PM (21:00 IST)", "Daily Egg Godown Inventory Report", "Daily text & PDF summary of egg production & godown stock sent to admins"),
    ("9:30 PM (21:30 IST)", "Sunfra Daily P&L Report", "Daily Profit & Loss financial performance report"),
    ("9:30 PM (21:30 IST)", "Egg Production Cross-Check Report", "Cross-checks daily egg production against book standards & flock benchmarks"),
    ("9:30 PM (21:30 IST)", "Feed Formula Approval Task Reminder", "Weekly approval reminder to team"),
    ("10:00 PM (22:00 IST)", "4-Company Consolidated Zoho Reconciliation Report", "Nightly consolidated reconciliation report sent to Kusum (7259510983)"),
    ("10:00 PM (22:00 IST)", "Daily Rental & Vacancy Loss Report", "Summary of vacant rental units & daily/MTD vacancy loss sent to Kusum"),
    ("10:00 PM (22:00 IST)", "Company-Wise Manager EOD Escalation Report", "EOD summary tracking pending vs completed reports across all teams"),
    ("11:00 PM (23:00 IST)", "Balaji Approval Task Reminder", "Reminder to Balaji to review & approve today's daily group report")
]

print("\nREMAINING REPORTS SCHEDULED FOR TODAY:")
for time_str, name, desc in schedules_today:
    print(f"• {time_str} - {name}: {desc}")
