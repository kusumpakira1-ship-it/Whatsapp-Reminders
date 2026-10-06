import sys, os
sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')

print("=== TESTING 4-COMPANY RECONCILIATION DISPATCH ===")

from zoho_reconciliation import (
    generate_and_send_zoho_reconciliation_report,
    generate_and_send_sunfra_feeds_reconciliation_report,
    generate_and_send_sunfra_corporate_reconciliation_report,
    generate_and_send_indus_reconciliation_report
)

recipient = "917259510983@c.us"

# Test 1: Sunfra Farms
try:
    print("Testing 1/4: Sunfra Farms...")
    res1 = generate_and_send_zoho_reconciliation_report(recipient)
    print(f"Sunfra Farms Result: {res1}")
except Exception as e:
    print(f"Sunfra Farms Error: {e}")

# Test 2: Sunfra Feeds
try:
    print("Testing 2/4: Sunfra Feeds...")
    res2 = generate_and_send_sunfra_feeds_reconciliation_report(recipient)
    print(f"Sunfra Feeds Result: {res2}")
except Exception as e:
    print(f"Sunfra Feeds Error: {e}")

# Test 3: Sunfra Corporate
try:
    print("Testing 3/4: Sunfra Corporate...")
    res3 = generate_and_send_sunfra_corporate_reconciliation_report(recipient)
    print(f"Sunfra Corporate Result: {res3}")
except Exception as e:
    print(f"Sunfra Corporate Error: {e}")

# Test 4: Indus
try:
    print("Testing 4/4: Indus...")
    res4 = generate_and_send_indus_reconciliation_report(recipient)
    print(f"Indus Result: {res4}")
except Exception as e:
    print(f"Indus Error: {e}")

print("=== TEST COMPLETE ===")
