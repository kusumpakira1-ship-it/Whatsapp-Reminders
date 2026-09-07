import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from zoho_reconciliation import generate_sunfra_farms_zoho_report, generate_sunfra_feeds_zoho_report, generate_sunfra_corporate_zoho_report

print("=== FARMS REPORT FOR 2026-09-03 ===")
farms_msg = generate_sunfra_farms_zoho_report('2026-09-03')
print(farms_msg[:600])

print("\n=== FEEDS REPORT FOR 2026-09-03 ===")
feeds_msg = generate_sunfra_feeds_zoho_report('2026-09-03')
print(feeds_msg[:600])

print("\n=== CORPORATE REPORT FOR 2026-09-03 ===")
corp_msg = generate_sunfra_corporate_zoho_report('2026-09-03')
print(corp_msg[:600])
