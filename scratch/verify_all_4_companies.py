import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.stdout.reconfigure(encoding='utf-8')

from zoho_service import get_access_token
from zoho_4company_pandl import fetch_today_sales_and_purchases
from zoho_reconciliation import format_today_sales_purchases_breakdown

access_token = get_access_token()

companies = [
    ("Sunfra Farms", "905812487"),
    ("Sunfra Feeds", "905813735"),
    ("Sunfra Corporate", "905813768"),
    ("Indus", "893416886")
]

for name, org_id in companies:
    sales_total, purch_total, sales_cnt, purch_cnt, sales_list, purch_list = fetch_today_sales_and_purchases(access_token, org_id, '2026-09-03')
    formatted = format_today_sales_purchases_breakdown(sales_total, purch_total, sales_cnt, purch_cnt, sales_list, purch_list)
    print(f"\n=================== {name} (Org: {org_id}) ===================")
    print(formatted)
