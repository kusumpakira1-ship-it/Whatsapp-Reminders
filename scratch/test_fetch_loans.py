import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')
from zoho_service import get_access_token, zoho_get, ZOHO_BOOKS_API_URL

access_token = get_access_token()
orgs = {
    'Sunfra Farms': '905812487',
    'Sunfra Feeds': '932776276',
    'Sunfra Corporate': '929124131',
    'Indus': '893416886'
}

def fetch_company_loans_from_balancesheet(access_token: str, org_id: str):
    url_bs = f"{ZOHO_BOOKS_API_URL}/reports/balancesheet?organization_id={org_id}"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    loans = []
    seen = set()
    
    try:
        res = zoho_get(url_bs, headers=headers, timeout=20)
        if res.status_code == 200:
            bs_data = res.json()
            
            def extract(node):
                if isinstance(node, dict):
                    name_str = (node.get('name') or node.get('account_name') or '').strip()
                    n_low = name_str.lower()
                    atype = str(node.get('account_type', '')).lower()
                    amt = float(node.get('total', 0) or node.get('balance', 0) or node.get('amount', 0) or 0.0)
                    
                    skip_keywords = ['accounts payable', 'liabilities', 'current liabilities', 'non current liabilities', 'other liabilities', 'liabilities & equities', 'equities', 'equity', 'finished goods', 'total']
                    if name_str and not any(n_low == k for k in skip_keywords):
                        is_loan = any(k in n_low for k in ['loan', 'od', 'overdraft', 'borrowing', 'finance']) or ('loan' in atype or 'borrowing' in atype)
                        if is_loan and abs(amt) > 0.01 and n_low not in seen:
                            seen.add(n_low)
                            loans.append((name_str, amt))
                            
                    for k, v in node.items():
                        if isinstance(v, (dict, list)):
                            extract(v)
                elif isinstance(node, list):
                    for item in node:
                        extract(item)
            extract(bs_data)
    except Exception as e:
        print(f"Error fetching balance sheet loans for org {org_id}: {e}")
        
    return loans

for name, org_id in orgs.items():
    print(f"\n=== {name} ===")
    loans = fetch_company_loans_from_balancesheet(access_token, org_id)
    if loans:
        print(f"💳 Loans & Liabilities ({len(loans)} active):")
        for lname, amt in loans:
            formatted_amt = f"-Rs. {abs(amt):,.2f}" if amt < 0 else f"Rs. {amt:,.2f}"
            print(f"  • {lname}: {formatted_amt}")
    else:
        print("💳 Loans & Liabilities: None ✅")
