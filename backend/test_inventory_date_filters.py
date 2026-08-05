import requests
from zoho_service import get_access_token, get_organization_id, ZOHO_BOOKS_API_URL

token = get_access_token()
org = get_organization_id(token)
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

for params in [
    "is_for_date_range=false",
    "filter_by=TransactionDate.AllTime",
    "filter_by=TransactionDate.ThisYear",
    "filter_by=TransactionDate.PreviousYear",
    "from_date=2025-01-01&to_date=2026-12-31"
]:
    url = f"{ZOHO_BOOKS_API_URL}/reports/inventorysummary?organization_id={org}&{params}&per_page=200"
    res = requests.get(url, headers=headers).json()
    items = res.get('inventory', [])
    code = res.get('code')
    msg = res.get('message')
    print(f"Filter [{params}] => Code: {code} | Count: {len(items)} | Msg: {msg}")
    if len(items) > 0 and code == 0:
        for i in items[:10]:
            name = i.get('item_name', '')
            qty = i.get('quantity_available', 0) or i.get('quantity_available_for_sale', 0) or 0
            if float(qty or 0) > 0 or 'egg' in name.lower() or 'godown' in name.lower():
                print(f"  --> Item: '{name}' | Qty: {qty} {i.get('unit')}")
