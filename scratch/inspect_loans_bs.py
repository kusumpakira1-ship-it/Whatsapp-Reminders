import sys, os, json, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))
from zoho_service import get_access_token, zoho_get, ZOHO_BOOKS_API_URL

access_token = get_access_token()

# Parse org IDs from zoho_reconciliation.py
with open(os.path.join(os.path.dirname(__file__), '..', 'backend', 'zoho_reconciliation.py'), 'r', encoding='utf-8') as f:
    text = f.read()
    org_matches = re.findall(r'(\w+_org_id)\s*=\s*"(\d+)"', text)
    print("Org IDs found in zoho_reconciliation.py:", org_matches)

# Map org IDs
orgs = {}
for var_name, oid in org_matches:
    if 'farms' in var_name: orgs['Sunfra Farms'] = oid
    elif 'feeds' in var_name: orgs['Sunfra Feeds'] = oid
    elif 'corp' in var_name: orgs['Sunfra Corporate'] = oid
    elif 'indus' in var_name: orgs['Indus'] = oid

for name, org_id in orgs.items():
    print(f"\n==================== {name} (Org: {org_id}) ====================")
    
    # 1. Fetch Chart of Accounts / Bank Accounts
    url_bank = f"{ZOHO_BOOKS_API_URL}/bankaccounts?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    res_b = zoho_get(url_bank, headers=headers, timeout=20)
    if res_b.status_code == 200:
        data = res_b.json().get('bankaccounts', [])
        print(f"Bank & Loan Accounts from /bankaccounts ({len(data)}):")
        for acc in data:
            aname = acc.get('account_name')
            atype = acc.get('account_type')
            bal = float(acc.get('bcy_balance', 0) or acc.get('balance', 0) or 0.0)
            print(f"  • [{atype}] {aname}: {bal:,.2f}")
            
    # 2. Fetch Balance Sheet Liabilities
    url_bs = f"{ZOHO_BOOKS_API_URL}/reports/balancesheet?organization_id={org_id}"
    res_bs = zoho_get(url_bs, headers=headers, timeout=20)
    if res_bs.status_code == 200:
        bs_data = res_bs.json()
        print("\n  Balance Sheet Liabilities Tree:")
        
        # Save BS JSON to scratch for inspection
        with open(os.path.join(os.path.dirname(__file__), f"bs_{name.replace(' ', '_')}.json"), 'w', encoding='utf-8') as f_out:
            json.dump(bs_data, f_out, indent=2)
            
        def find_liabilities(node, depth=0):
            if isinstance(node, dict):
                name_str = (node.get('name') or node.get('account_name') or '').strip()
                n_low = name_str.lower()
                atype = str(node.get('account_type', '')).lower()
                amt = float(node.get('total', 0) or node.get('balance', 0) or node.get('amount', 0) or 0.0)
                
                is_liab = any(k in n_low for k in ['loan', 'od', 'overdraft', 'borrowing', 'liability', 'liabilities', 'credit card', 'payable', 'equity']) or ('liability' in atype or 'loan' in atype)
                if is_liab and name_str:
                    print(f"    {'  ' * depth}-> {name_str} (Type: {atype}): {amt:,.2f}")
                    
                for k, v in node.items():
                    if isinstance(v, (dict, list)):
                        find_liabilities(v, depth+1)
            elif isinstance(node, list):
                for item in node:
                    find_liabilities(item, depth)
                    
        find_liabilities(bs_data)
