import sys, os, time
sys.path.insert(0, os.path.abspath('backend'))
sys.stdout.reconfigure(encoding='utf-8')

from zoho_reconciliation import (
    generate_and_send_zoho_reconciliation_report,
    generate_and_send_sunfra_feeds_reconciliation_report,
    generate_and_send_sunfra_corporate_reconciliation_report,
    generate_and_send_indus_reconciliation_report
)

recipient = "917259510983@c.us"

print("--- 1. Testing Sunfra Farms ---")
t0 = time.time()
try:
    r1 = generate_and_send_zoho_reconciliation_report(recipient)
    print(f"Farms: {r1} ({time.time()-t0:.1f}s)")
except Exception as e:
    print("Farms error:", e)

print("--- 2. Testing Sunfra Feeds ---")
t0 = time.time()
try:
    r2 = generate_and_send_sunfra_feeds_reconciliation_report(recipient)
    print(f"Feeds: {r2} ({time.time()-t0:.1f}s)")
except Exception as e:
    print("Feeds error:", e)

print("--- 3. Testing Sunfra Corporate ---")
t0 = time.time()
try:
    r3 = generate_and_send_sunfra_corporate_reconciliation_report(recipient)
    print(f"Corporate: {r3} ({time.time()-t0:.1f}s)")
except Exception as e:
    print("Corporate error:", e)

print("--- 4. Testing Indus ---")
t0 = time.time()
try:
    r4 = generate_and_send_indus_reconciliation_report(recipient)
    print(f"Indus: {r4} ({time.time()-t0:.1f}s)")
except Exception as e:
    print("Indus error:", e)
