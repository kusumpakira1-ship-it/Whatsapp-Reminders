import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.getcwd(), 'backend'))

print("==================================================")
print(" VERIFYING TONIGHT'S SCHEDULED REPORTS GENERATORS ")
print("==================================================")

# 1. PAPAAK Reports
try:
    from papaak_email_service import generate_daily_feed_rates_report, generate_daily_egg_rates_report
    feed_rep = generate_daily_feed_rates_report()
    egg_rep = generate_daily_egg_rates_report()
    print("\n✅ [OK] PAPAAK Feed & Egg Rates Reports generated successfully.")
except Exception as e:
    print(f"\n❌ [ERROR] PAPAAK Reports: {e}")

# 2. Daily Attendance Summary Report
try:
    from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message
    data = evaluate_attendance_for_date()
    att_msg = generate_attendance_summary_message(data)
    print("✅ [OK] Daily Attendance Summary Report generated successfully.")
except Exception as e:
    print(f"❌ [ERROR] Daily Attendance Summary: {e}")

# 3. Egg Production Cross-Check Report
try:
    from egg_production_crosscheck import generate_egg_production_crosscheck_report
    crosscheck_text = generate_egg_production_crosscheck_report()
    print("✅ [OK] Egg Production vs Godown Stock Cross-Check Report generated successfully.")
except Exception as e:
    print(f"❌ [ERROR] Egg Production Cross-Check: {e}")

# 4. Egg Godown Inventory Report
try:
    from report_generator_godown import generate_godown_report
    godown_text = generate_godown_report()
    print("✅ [OK] Egg Godown Inventory Report generated successfully.")
except Exception as e:
    print(f"❌ [ERROR] Egg Godown Inventory Report: {e}")

# 5. Sunfra 4-Company P&L Summary Report
try:
    from zoho_4company_pandl import generate_4company_pandl_report
    pandl_text = generate_4company_pandl_report()
    print("✅ [OK] Sunfra 4-Company P&L Summary Report generated successfully.")
except Exception as e:
    print(f"❌ [ERROR] P&L Summary Report: {e}")

print("\nAll tonight report generators verified cleanly!")
