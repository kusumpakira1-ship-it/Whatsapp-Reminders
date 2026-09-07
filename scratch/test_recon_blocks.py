import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from zoho_reconciliation import extract_physical_balances_from_whatsapp, format_reconciliation_block, get_chart_of_accounts, get_access_token

access_token = get_access_token()
farms_org_id = "905812487"
accounts = get_chart_of_accounts(access_token, farms_org_id)
physical = extract_physical_balances_from_whatsapp('Accounts Poultry', '2026-09-03')

print("=== FARMS PHYSICAL FROM WA 2026-09-03 ===")
print("Physical dict:", physical)
print("\n=== ZOHO ACCOUNTS ===")
print("Petty cash zoho:", accounts.get('petty_cash'))
print("Bank zoho:", accounts.get('sunfra_farms_bank'))
print("SBI loan zoho:", accounts.get('sbi_term_loan'))
print("OD zoho:", accounts.get('sunfra_farm_od'))

print("\n=== RECONCILIATION BLOCKS FOR FARMS ON 2026-09-03 ===")
print(format_reconciliation_block("Petty Cash", physical.get('petty_cash'), accounts.get('petty_cash', 0.0)))
print(format_reconciliation_block("SUNFRA FARMS Bank", physical.get('sunfra_farms_bank'), accounts.get('sunfra_farms_bank', 0.0)))
print(format_reconciliation_block("SBI TERM LOAN ACCOUNT (5637)", physical.get('sbi_term_loan'), accounts.get('sbi_term_loan', 0.0)))
print(format_reconciliation_block("SUNFRA FARM OD-0718 (0718)", physical.get('sunfra_farm_od'), accounts.get('sunfra_farm_od', 0.0)))
