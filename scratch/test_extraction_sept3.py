import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from zoho_reconciliation import extract_physical_balances_from_whatsapp

for grp in ['Accounts Poultry', 'Summary - Sunfra Feeds', 'Sunfra Corporate P&L']:
    res = extract_physical_balances_from_whatsapp(grp, '2026-09-03')
    print(f"Physical balances extracted for '{grp}' on 2026-09-03:")
    print(" ", res)
    print("=" * 60)
