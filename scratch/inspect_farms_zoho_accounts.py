"""
Inspect Zoho Books Chart of Accounts for Sunfra Farms
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

from zoho_service import get_access_token, get_organization_id, get_chart_of_accounts

access_token = get_access_token()
farms_org_id = get_organization_id(access_token)

print(f"Farms Org ID: {farms_org_id}")
accounts = get_chart_of_accounts(access_token, farms_org_id)
print("=== ACCOUNTS RETURNED ===")
print(accounts)
