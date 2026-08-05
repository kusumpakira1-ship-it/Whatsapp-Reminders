import requests
from zoho_service import get_access_token, get_organization_id, ZOHO_BOOKS_API_URL

token = get_access_token()
org = get_organization_id(token)
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

print("=== FETCHING ALL ITEMS FROM ZOHO BOOKS ===")
page = 1
has_more = True
all_items = []

while has_more and page <= 25:
    url = f"{ZOHO_BOOKS_API_URL}/items?organization_id={org}&page={page}&per_page=200"
    res = requests.get(url, headers=headers).json()
    items = res.get('items', [])
    all_items.extend(items)
    
    page_ctx = res.get('page_context', {})
    has_more = page_ctx.get('has_more_page', False)
    page += 1

print(f"\nTotal Items in Zoho Books: {len(all_items)}")

tracked_items = [i for i in all_items if i.get('is_tracked', False) or i.get('track_inventory', False) or float(i.get('stock_on_hand', 0) or 0) > 0]
print(f"Total Tracked / Non-Zero Stock Items: {len(tracked_items)}")

print("\n--- ITEMS WITH NON-ZERO STOCK OR TRACKED ---")
for i in tracked_items[:30]:
    print(f"ID: {i.get('item_id')} | Name: '{i.get('name')}' | Stock: {i.get('stock_on_hand')} {i.get('unit')} | Rate: Rs. {i.get('rate')}")

print("\n--- SEARCHING FOR EGG / GODOWN / FARM / FEED IN ALL ITEMS ---")
matches = [i for i in all_items if any(k in i.get('name', '').lower() for k in ['egg', 'godown', 'farm', 'feed', 'chick', 'tray', 'layer', 'bird'])]
if matches:
    for m in matches:
        print(f"ID: {m.get('item_id')} | Name: '{m.get('name')}' | Stock: {m.get('stock_on_hand')} {m.get('unit')} | Tracked: {m.get('is_tracked') or m.get('track_inventory')}")
else:
    print("No items matching 'egg', 'godown', 'farm', 'feed', 'chick', or 'tray' found in any of the items.")
