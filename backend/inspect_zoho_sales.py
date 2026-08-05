import requests
from datetime import datetime, timezone, timedelta
from zoho_service import get_access_token, ZOHO_BOOKS_API_URL

token = get_access_token()
org = "905812487"  # Sunfra Farms
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

IST = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(IST).strftime("%Y-%m-%d")

print(f"=== FETCHING ZOHO SALES INVOICES FOR SUNFRA FARMS ({org}) ===")
url = f"{ZOHO_BOOKS_API_URL}/invoices?organization_id={org}&per_page=200"
res = requests.get(url, headers=headers).json()

invoices = res.get('invoices', [])
print(f"Total Invoices in Zoho: {len(invoices)}")

today_sales = []
total_sales_trays = 0.0
total_sales_amount = 0.0

for inv in invoices:
    inv_date = inv.get('date', '')
    customer = inv.get('customer_name', '')
    total = float(inv.get('total', 0) or 0.0)
    inv_num = inv.get('invoice_number', '')
    status = inv.get('status', '')
    
    if inv_date == today_str or True: # inspect recent
        today_sales.append({
            'num': inv_num,
            'date': inv_date,
            'customer': customer,
            'amount': total,
            'status': status
        })
        total_sales_amount += total

print("\n--- RECENT ZOHO SALES INVOICES (SUNFRA FARMS) ---")
for s in today_sales[:10]:
    print(f"Date: {s['date']} | Inv#: {s['num']} | Customer: '{s['customer']}' | Amount: Rs. {s['amount']:,.2f} | Status: {s['status']}")

print(f"\nTotal Recent Sales Amount in Zoho: Rs. {total_sales_amount:,.2f}")
