import sys

sys.path.append('backend')
from zoho_reconciliation import extract_physical_balances_from_whatsapp

sys.stdout.reconfigure(encoding='utf-8')

print("================ TESTING PHYSICAL BALANCE PARSING FOR YESTERDAY (16 SEP) ================")

for grp in ['Accounts Poultry', 'Summary - Sunfra Feeds', 'Sunfra Corporate P&L']:
    parsed = extract_physical_balances_from_whatsapp(grp, target_date="2026-09-16")
    print(f"\nGroup '{grp}' extracted balances:")
    for k, v in parsed.items():
        if v is not None:
            print(f"  • {k}: {v:,.2f}")
        else:
            print(f"  • {k}: None")

db_session = None
