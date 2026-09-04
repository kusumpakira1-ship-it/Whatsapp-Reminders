import sys
import os

sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

print("==================================================")
print("DISPATCHING ALL REPORTS NOW TO 7259510983")
print("==================================================")

target_phone = "917259510983@c.us"

# 1. Zoho Reconciliation Reports (All 3)
print("\n[1/7] Sending 3 Zoho Reconciliation Reports...")
try:
    from zoho_reconciliation import (
        generate_and_send_zoho_reconciliation_report,
        generate_and_send_sunfra_feeds_reconciliation_report,
        generate_and_send_sunfra_corporate_reconciliation_report
    )
    generate_and_send_zoho_reconciliation_report(target_phone)
    generate_and_send_sunfra_feeds_reconciliation_report(target_phone)
    generate_and_send_sunfra_corporate_reconciliation_report(target_phone)
    print("  ✅ 3 Zoho Reconciliation Reports dispatched!")
except Exception as e:
    print(f"  ❌ Error sending Zoho Reconciliation Reports: {e}")

# 2. Sunfra Daily P&L Report
print("\n[2/7] Sending Sunfra Daily P&L Report...")
try:
    from sunfra_pandl_report import generate_and_send_sunfra_pandl_report
    generate_and_send_sunfra_pandl_report([target_phone])
    print("  ✅ Sunfra Daily P&L Report dispatched!")
except Exception as e:
    print(f"  ❌ Error sending Sunfra P&L Report: {e}")

# 3. 4-Company P&L & Stock Report
print("\n[3/7] Sending 4-Company P&L & Stock Report...")
try:
    from zoho_4company_pandl import generate_and_send_4company_pandl_report
    generate_and_send_4company_pandl_report(target_phone)
    print("  ✅ 4-Company P&L Report dispatched!")
except Exception as e:
    print(f"  ❌ Error sending 4-Company P&L Report: {e}")

# 4. Daily Egg Market & Price Analysis PDF Report
print("\n[4/7] Sending Daily Egg Market PDF Report...")
try:
    from egg_market_analyzer import send_daily_egg_market_pdf_job
    send_daily_egg_market_pdf_job()
    print("  ✅ Daily Egg Market PDF Report dispatched!")
except Exception as e:
    print(f"  ❌ Error sending Egg Market PDF Report: {e}")

# 5. Daily Farm Summary Report (Mortality, Production 96+%, Birds Weight)
print("\n[5/7] Sending Daily Farm Summary Report...")
try:
    from daily_farm_summary import send_daily_farm_summary_1155pm_job
    send_daily_farm_summary_1155pm_job()
    print("  ✅ Daily Farm Summary Report dispatched!")
except Exception as e:
    print(f"  ❌ Error sending Daily Farm Summary Report: {e}")

# 6. Daily Egg Godown Summary Report
print("\n[6/7] Sending Daily Egg Godown Summary Report...")
try:
    from scheduler import scheduled_godown_report_job
    scheduled_godown_report_job()
    print("  ✅ Daily Egg Godown Summary Report dispatched!")
except Exception as e:
    print(f"  ❌ Error sending Daily Egg Godown Report: {e}")

# 7. Rental & Vacancy Summary Report
print("\n[7/7] Sending Rental & Vacancy Summary Report...")
try:
    from vacancy_processor import generate_vacancy_summary
    from waha_service import send_waha_message
    summary_text = generate_vacancy_summary()
    send_waha_message(target_phone, summary_text)
    print("  ✅ Rental & Vacancy Summary Report dispatched!")
except Exception as e:
    print(f"  ❌ Error sending Vacancy Summary Report: {e}")

print("\n==================================================")
print("ALL DISPATCHES COMPLETED TO 7259510983!")
print("==================================================")
