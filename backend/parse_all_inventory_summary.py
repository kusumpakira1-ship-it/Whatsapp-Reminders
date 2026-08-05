import requests
from zoho_service import get_access_token, get_organization_id, ZOHO_BOOKS_API_URL

token = get_access_token()
org = get_organization_id(token)
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

print("=== FETCHING ALL PAGES OF ZOHO INVENTORY SUMMARY REPORT ===")
page = 1
has_more = True
total_items = 0
non_zero_items = []
egg_related_items = []

while has_more and page <= 20:
    url = f"{ZOHO_BOOKS_API_URL}/reports/inventorysummary?organization_id={org}&page={page}&per_page=200&filter_by=Status.All"
    res = requests.get(url, headers=headers).json()
    
    if 'inventory' in res:
        for item in res['inventory']:
            total_items += 1
            name = item.get('item_name', '')
            qty = float(item.get('quantity_available', 0) or item.get('quantity_available_for_sale', 0) or 0)
            purchased = float(item.get('quantity_purchased', 0) or 0)
            sold = float(item.get('quantity_sold', 0) or 0)
            unit = item.get('unit', '')
            
            if qty > 0 or purchased > 0 or sold > 0:
                non_zero_items.append({
                    'name': name,
                    'qty_available': qty,
                    'purchased': purchased,
                    'sold': sold,
                    'unit': unit
                })
            if any(k in name.lower() for k in ['egg', 'godown', 'farm', 'tray', 'chick', 'feed', 'layer', 'bird']):
                egg_related_items.append({
                    'name': name,
                    'qty_available': qty,
                    'unit': unit
                })
                    
        page_ctx = res.get('page_context', {})
        has_more = page_ctx.get('has_more_page', False)
        page += 1
    else:
        print("End or Error:", res.get('message', res))
        break

print(f"\nTotal Inventory Items Scanned: {total_items}")
print(f"Total Active Items with Stock/Activity: {len(non_zero_items)}")

print("\n--- TOP 20 ITEMS WITH HIGHEST AVAILABLE STOCK IN ZOHO INVENTORY SUMMARY ---")
for i in sorted(non_zero_items, key=lambda x: x['qty_available'], reverse=True)[:20]:
    print(f"Item: '{i['name']}' | Qty Available: {i['qty_available']} {i['unit']} | Purchased: {i['purchased']} | Sold: {i['sold']}")

print("\n--- ALL EGG / FARM / FEED / CHICK RELATED ITEMS IN ZOHO INVENTORY SUMMARY ---")
if egg_related_items:
    for e in egg_related_items:
        print(f"Item: '{e['name']}' | Qty Available: {e['qty_available']} {e['unit']}")
else:
    print("No items matching 'egg', 'godown', 'farm', 'feed', 'chick', or 'tray' found in Inventory Summary.")
