import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_dir = os.path.join(repo_root, 'backend')
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

os.environ["WAHA_URL"] = "http://localhost:3000"
from backend.config import settings
settings.WAHA_URL = "http://localhost:3000"

from zoho_reconciliation import (
    generate_and_send_zoho_reconciliation_report,
    generate_and_send_sunfra_feeds_reconciliation_report,
    generate_and_send_sunfra_corporate_reconciliation_report
)
from zoho_4company_pandl import generate_and_send_4company_pandl_report

TARGET_PHONE = "917259510983@c.us"

print(f"=== TESTING INDIAN CURRENCY FORMAT & OD DESCENDING SORT FOR {TARGET_PHONE} ===")

print("\n--- 1. SENDING 3-COMPANY ZOHO RECONCILIATION REPORTS ---")
generate_and_send_zoho_reconciliation_report(TARGET_PHONE)
generate_and_send_sunfra_feeds_reconciliation_report(TARGET_PHONE)
generate_and_send_sunfra_corporate_reconciliation_report(TARGET_PHONE)
print("  -> Sent 3-Company Zoho Reconciliation Reports!")

print("\n--- 2. SENDING 4-COMPANY P&L & STOCK REPORTS ---")
generate_and_send_4company_pandl_report(TARGET_PHONE)
print("  -> Sent 4-Company Daily P&L & Stock Reports!")

print("\n=== DISPATCH COMPLETE ===")
