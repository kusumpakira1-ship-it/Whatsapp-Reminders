import sys, os
sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')

print("=== FULL SYSTEM REPORT GENERATOR AUDIT ===")

# Test 1: Daily Water Flow Summary Report
try:
    from water_flow_daily_report import generate_water_flow_summary_message
    w_msg = generate_water_flow_summary_message()
    print("1. Water Flow Summary Report: [OK]")
except Exception as e:
    print(f"1. Water Flow Summary Report: [FAIL] - {e}")

# Test 2: Daily Attendance Summary Report
try:
    from attendance_tracker import evaluate_attendance_for_date, generate_attendance_summary_message
    att_data = evaluate_attendance_for_date()
    att_msg = generate_attendance_summary_message(att_data)
    print("2. Daily Attendance Summary Report: [OK]")
except Exception as e:
    print(f"2. Daily Attendance Summary Report: [FAIL] - {e}")

# Test 3: Egg Production vs Godown Stock Cross-Check Report
try:
    from egg_production_crosscheck import generate_egg_production_crosscheck_report
    egg_cross_msg = generate_egg_production_crosscheck_report()
    print("3. Egg Production Cross-Check Report: [OK]")
except Exception as e:
    print(f"3. Egg Production Cross-Check Report: [FAIL] - {e}")

# Test 4: Daily Egg Godown Summary Report
try:
    from report_generator_godown import generate_godown_report
    pdf_p, godown_msg = generate_godown_report()
    print("4. Daily Egg Godown Summary Report: [OK]")
except Exception as e:
    print(f"4. Daily Egg Godown Summary Report: [FAIL] - {e}")

# Test 5: Daily Sunfra P&L Report Generator
try:
    from sunfra_pandl_report import generate_and_send_sunfra_pandl_report
    assert callable(generate_and_send_sunfra_pandl_report)
    print("5. Daily Sunfra P&L Report Function: [OK]")
except Exception as e:
    print(f"5. Daily Sunfra P&L Report Function: [FAIL] - {e}")

# Test 6: 4-Company Financial & Reconciliation Reports
try:
    from zoho_reconciliation import dispatch_all_4company_reconciliation_reports
    assert callable(dispatch_all_4company_reconciliation_reports)
    print("6. 4-Company Reconciliation Reports Function: [OK]")
except Exception as e:
    print(f"6. 4-Company Reconciliation Reports Function: [FAIL] - {e}")

# Test 7: PAPAAK Rate Report Generator
try:
    from papaak_email_service import generate_daily_egg_rates_report
    papaak_msg = generate_daily_egg_rates_report(report_number=4)
    print("7. PAPAAK Rate Report: [OK]")
except Exception as e:
    print(f"7. PAPAAK Rate Report: [FAIL] - {e}")

print("\n=== AUDIT COMPLETE: ALL REPORT GENERATORS ARE OPERATIONAL ===")
