import requests
from datetime import datetime, timezone, timedelta
from zoho_service import get_access_token, get_organization_id, ZOHO_BOOKS_API_URL

token = get_access_token()
org = get_organization_id(token)
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

IST = timezone(timedelta(hours=5, minutes=30))
today_str = datetime.now(IST).strftime("%Y-%m-%d")

print(f"=== 1. ZOHO SALES INVOICES (QUANTITY OUT) FOR ORG {org} ===")
url_inv = f"{ZOHO_BOOKS_API_URL}/invoices?organization_id={org}&per_page=200"
res_inv = requests.get(url_inv, headers=headers).json()

invoices = res_inv.get('invoices', [])
print(f"Total Sales Invoices Found in Zoho: {len(invoices)}")

today_sales_trays = 0.0
today_sales_amount = 0.0
total_sales_trays = 0.0
total_sales_amount = 0.0

for inv in invoices:
    date_str = inv.get('date', '')
    amt = float(inv.get('total', 0) or 0)
    total_sales_amount += amt
    
    if date_str == today_str:
        today_sales_amount += amt

print(f"Total Sales Invoices Amount: Rs. {total_sales_amount:,.2f}")
print(f"Today's ({today_str}) Sales Invoices Amount: Rs. {today_sales_amount:,.2f}")

print("\n=== 2. ZOHO ITEM SALES SUMMARY REPORT ===")
url_report = f"{ZOHO_BOOKS_API_URL}/reports/itemsalessummary?organization_id={org}"
res_report = requests.get(url_report, headers=headers).json()

if 'item_sales_summary' in res_report:
    print("Item Sales Summary Found:")
    for row in res_report['item_sales_summary'][:15]:
        name = row.get('item_name', '')
        qty = row.get('quantity_sold', 0)
        amt = row.get('amount', 0)
        print(f"  • Item: '{name}' | Qty Sold (Out): {qty} | Total Sales: Rs. {amt:,.2f}")
else:
    print("Item Sales Report response keys:", list(res_report.keys()))

print("\n=== 3. RECENT 5 SALES INVOICES IN ZOHO ===")
for inv in invoices[:5]:
    inv_id = inv.get('invoice_id')
    inv_num = inv.get('invoice_number')
    cust = inv.get('customer_name')
    date = inv.get('date')
    tot = inv.get('total')
    print(f"Inv #{inv_num} | Date: {date} | Customer: {cust} | Amount: Rs. {tot}")
