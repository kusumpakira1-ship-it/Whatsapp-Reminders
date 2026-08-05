import requests
from zoho_service import get_access_token, get_organization_id, ZOHO_BOOKS_API_URL

token = get_access_token()
org = get_organization_id(token)
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

url = f"{ZOHO_BOOKS_API_URL}/invoices?organization_id={org}&per_page=10"
res = requests.get(url, headers=headers).json()
invoices = res.get('invoices', [])

print(f"=== INSPECTING LINE ITEMS FOR RECENT {len(invoices)} INVOICES ===")
for inv_summary in invoices:
    inv_id = inv_summary.get('invoice_id')
    inv_detail = requests.get(f"{ZOHO_BOOKS_API_URL}/invoices/{inv_id}?organization_id={org}", headers=headers).json().get('invoice', {})
    
    print(f"\nInv #{inv_detail.get('invoice_number')} | Date: {inv_detail.get('date')} | Customer: {inv_detail.get('customer_name')} | Total: Rs. {inv_detail.get('total')}")
    for item in inv_detail.get('line_items', []):
        print(f"   • Item: '{item.get('name')}' | Qty: {item.get('quantity')} {item.get('unit')} | Rate: Rs. {item.get('rate')} | Line Total: Rs. {item.get('item_total')}")
