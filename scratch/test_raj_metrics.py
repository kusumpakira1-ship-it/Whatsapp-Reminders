import sys
import requests
import json
sys.stdout.reconfigure(encoding='utf-8')

token = '1000.8d220264e57b0769d33d563af8ad6e60.00c8c5adc99a673bed450fe928460800'
headers = {'Authorization': f'Zoho-oauthtoken {token}'}
org_id = '904503869'

try:
    res_inv = requests.get(f'https://www.zohoapis.com/books/v3/invoices?organization_id={org_id}&status=unpaid', headers=headers, timeout=10).json()
    invoices = res_inv.get('invoices', [])
    print(f"Unpaid Invoices Count: {len(invoices)}", flush=True)
    tot_rec = sum(float(inv.get('balance', 0)) for inv in invoices)
    print(f"Total Receivables: {tot_rec}", flush=True)
except Exception as e:
    print(f"Invoice error: {e}", flush=True)

try:
    res_bills = requests.get(f'https://www.zohoapis.com/books/v3/bills?organization_id={org_id}&status=unpaid', headers=headers, timeout=10).json()
    bills = res_bills.get('bills', [])
    print(f"Unpaid Bills Count: {len(bills)}", flush=True)
    tot_pay = sum(float(b.get('balance', 0)) for b in bills)
    print(f"Total Payables: {tot_pay}", flush=True)
except Exception as e:
    print(f"Bill error: {e}", flush=True)

try:
    res_items = requests.get(f'https://www.zohoapis.com/books/v3/items?organization_id={org_id}', headers=headers, timeout=10).json()
    items = res_items.get('items', [])
    print(f"Items in inventory: {len(items)}", flush=True)
    for it in items[:5]:
        print(f"- {it.get('name')}: Stock={it.get('stock_on_hand')} {it.get('unit')}", flush=True)
except Exception as e:
    print(f"Item error: {e}", flush=True)
