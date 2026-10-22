import sys
import os

print("==================================================")
print("COMPREHENSIVE TEST OF ALL SCHEDULED REPORTS")
print("==================================================")

# 1. 6:50 PM & 9:30 PM: Egg Production Cross-Check
print("\n--- 1. Egg Production Cross-Check Report ---")
try:
    from egg_production_crosscheck import generate_egg_production_crosscheck_report
    rep1 = generate_egg_production_crosscheck_report()
    print("SUCCESS! Output length:", len(rep1))
    print("Preview:\n" + rep1[:150] + "...")
except Exception as e:
    print("FAILED:", e)

# 2. 6:55 PM & 8:30 PM: Sunfra Farms Summary Report
print("\n--- 2. Sunfra Farms Summary Report ---")
try:
    from sunfra_farms_summary_report import generate_sunfra_farms_summary_report
    rep2 = generate_sunfra_farms_summary_report()
    print("SUCCESS! Output length:", len(rep2))
    print("Preview:\n" + rep2[:150] + "...")
except Exception as e:
    print("FAILED:", e)

# 3. 9:00 PM: Egg Godown Summary Report
print("\n--- 3. Egg Godown Summary Report ---")
try:
    from report_generator_godown import generate_godown_report
    pdf3, rep3 = generate_godown_report()
    print(f"SUCCESS! PDF: {pdf3}, Text len: {len(rep3) if rep3 else 0}")
    if rep3:
        print("Preview:\n" + rep3[:150] + "...")
except Exception as e:
    print("FAILED:", e)

# 4. 9:30 PM: Sunfra P&L Report
print("\n--- 4. Sunfra P&L Report ---")
try:
    import sunfra_pandl_report
    print("Functions in sunfra_pandl_report:", [f for f in dir(sunfra_pandl_report) if 'generate' in f or 'report' in f])
    from sunfra_pandl_report import generate_sunfra_pandl_pdf
    pdf4 = generate_sunfra_pandl_pdf()
    print(f"SUCCESS! PDF: {pdf4}")
except Exception as e:
    print("FAILED:", e)

# 5. 6:50 PM / 10:30 PM / 11:50 PM: 4 Consolidated Company Reports (Zoho Reconciliation)
print("\n--- 5. 4-Company Zoho Reconciliation Reports ---")
try:
    from zoho_reconciliation import (
        generate_and_send_zoho_reconciliation_report,
        generate_and_send_sunfra_feeds_reconciliation_report,
        generate_and_send_sunfra_corporate_reconciliation_report,
        generate_and_send_indus_reconciliation_report
    )
    print("Zoho reconciliation functions loaded successfully.")
    # Dry run org id fetching
    from zoho_service import get_organization_id
    for comp in ["Sunfra Farms", "Sunfra Feeds", "Corporate Eggs", "Indus Poultry Equipments Pvt Ltd"]:
        oid = get_organization_id(comp)
        print(f"  Org '{comp}': {oid}")
except Exception as e:
    print("FAILED:", e)

# 6. 10:30 PM & 11:50 PM: Daily Rental Vacancy Loss Report
print("\n--- 6. Rental & Vacancy Loss Report ---")
try:
    from scheduler import generate_rental_vacancy_report
    rep6 = generate_rental_vacancy_report()
    print("SUCCESS! Output length:", len(rep6) if rep6 else 0)
    if rep6:
        print("Preview:\n" + rep6[:150] + "...")
except Exception as e:
    print("FAILED:", e)

# 7. 10:30 PM & 11:50 PM: Company-Wise Manager Escalation EOD Summary
print("\n--- 7. Company-Wise Manager Escalation EOD Summary ---")
try:
    from scheduler import generate_company_wise_escalation_summary
    rep7 = generate_company_wise_escalation_summary()
    print("SUCCESS! Output length:", len(rep7) if rep7 else 0)
    if rep7:
        print("Preview:\n" + rep7[:150] + "...")
except Exception as e:
    print("FAILED:", e)

# 8. 11:45 PM: Daily Attendance Summary Report
print("\n--- 8. Daily Attendance Summary Report ---")
try:
    from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message, generate_company_attendance_messages
    att_data = evaluate_attendance_for_date()
    rep8 = generate_attendance_summary_message(att_data)
    print("SUCCESS! Output length:", len(rep8))
    print("Preview:\n" + rep8[:150] + "...")
except Exception as e:
    print("FAILED:", e)

# 9. 11:58 PM: Daily Water Flow Summary Report
print("\n--- 9. Daily Water Flow Summary Report ---")
try:
    from water_flow_daily_report import generate_daily_water_flow_report
    rep9 = generate_daily_water_flow_report()
    print("SUCCESS! Output length:", len(rep9) if rep9 else 0)
    if rep9:
        print("Preview:\n" + rep9[:150] + "...")
except Exception as e:
    print("FAILED:", e)

print("\n==================================================")
print("TEST COMPLETE")
print("==================================================")
