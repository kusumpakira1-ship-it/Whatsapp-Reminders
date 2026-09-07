import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from zoho_reconciliation import (
    generate_and_send_zoho_reconciliation_report,
    generate_and_send_sunfra_feeds_reconciliation_report,
    generate_and_send_sunfra_corporate_reconciliation_report,
    generate_and_send_indus_reconciliation_report
)

print("=== TESTING DISPATCH OF ALL 4 REPORTS INDIVIDUALLY ===")

print("\n--- 1. FARMS REPORT ---")
try:
    res1 = generate_and_send_zoho_reconciliation_report("917259510983@c.us")
    print("Farms result:", res1)
except Exception as e:
    print("Farms ERROR:", e)

print("\n--- 2. FEEDS REPORT ---")
try:
    res2 = generate_and_send_sunfra_feeds_reconciliation_report("917259510983@c.us")
    print("Feeds result:", res2)
except Exception as e:
    print("Feeds ERROR:", e)

print("\n--- 3. CORPORATE REPORT ---")
try:
    res3 = generate_and_send_sunfra_corporate_reconciliation_report("917259510983@c.us")
    print("Corporate result:", res3)
except Exception as e:
    print("Corporate ERROR:", e)

print("\n--- 4. INDUS REPORT ---")
try:
    res4 = generate_and_send_indus_reconciliation_report("917259510983@c.us")
    print("Indus result:", res4)
except Exception as e:
    print("Indus ERROR:", e)
