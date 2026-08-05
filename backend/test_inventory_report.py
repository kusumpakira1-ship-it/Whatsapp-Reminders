import requests
from zoho_service import get_access_token, get_organization_id, ZOHO_BOOKS_API_URL

token = get_access_token()
org = get_organization_id(token)
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

url = f"{ZOHO_BOOKS_API_URL}/reports/inventorysummary?organization_id={org}&show_actual_stock=true"
res = requests.get(url, headers=headers).json()

items = res.get('inventory', [])
print(f"Total Items fetched with show_actual_stock=true: {len(items)}")

non_zero = []
for i in items:
    qty = float(i.get('quantity_available', 0) or i.get('quantity_available_for_sale', 0) or 0)
    purchased = float(i.get('quantity_purchased', 0) or 0)
    sold = float(i.get('quantity_sold', 0) or 0)
    name = i.get('item_name', '')
    if qty > 0 or purchased > 0 or sold > 0:
        non_zero.append(f"Name: '{name}' | Qty Available: {qty} {i.get('unit')} | Purchased: {purchased} | Sold: {sold}")

print(f"\nNon-zero active items count: {len(non_zero)}")
for nz in non_zero[:30]:
    print(nz)
