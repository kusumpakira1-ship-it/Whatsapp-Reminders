import requests
from zoho_service import get_access_token, get_organization_id, ZOHO_BOOKS_API_URL

token = get_access_token()
org = get_organization_id(token)
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

print("=== 1. ALL ZOHO ITEMS ===")
items_res = requests.get(f'{ZOHO_BOOKS_API_URL}/items?organization_id={org}', headers=headers).json()
for i in items_res.get('items', []):
    print(f"ID: {i.get('item_id')} | Name: '{i.get('name')}' | Stock: {i.get('stock_on_hand')} | Unit: '{i.get('unit')}' | Rate: {i.get('rate')}")

print("\n=== 2. ALL ZOHO BANK & CASH ACCOUNTS ===")
bank_res = requests.get(f'{ZOHO_BOOKS_API_URL}/bankaccounts?organization_id={org}', headers=headers).json()
for b in bank_res.get('bankaccounts', []):
    print(f"Name: '{b.get('account_name')}' | Type: '{b.get('account_type')}' | Balance: {b.get('balance')} | Uncat: {b.get('uncategorized_transactions')}")

print("\n=== 3. CHART OF ACCOUNTS (LOANS / OD / FARMS) ===")
coa_res = requests.get(f'{ZOHO_BOOKS_API_URL}/chartofaccounts?organization_id={org}', headers=headers).json()
for c in coa_res.get('chartofaccounts', []):
    name = c.get('account_name', '')
    acc_type = c.get('account_type', '')
    bal = c.get('balance', 0)
    if any(k in name.lower() or k in acc_type.lower() for k in ['loan', 'od', 'overdraft', 'petty', 'cash', 'farm', 'godown', 'egg']):
        print(f"Name: '{name}' | Type: '{acc_type}' | Balance: {bal}")

print("\n=== 4. UNPAID INVOICES (RECEIVABLES) ===")
inv_res = requests.get(f'{ZOHO_BOOKS_API_URL}/invoices?organization_id={org}&status=unpaid', headers=headers).json()
invoices = inv_res.get('invoices', [])
print(f"Total Unpaid Invoices Count: {len(invoices)}")
total_inv_bal = sum(float(i.get('balance', 0) or 0) for i in invoices)
print(f"Total Unpaid Invoices Balance: Rs. {total_inv_bal:,.2f}")
for inv in invoices[:5]:
    print(f"  Inv#: {inv.get('invoice_number')} | Customer: {inv.get('customer_name')} | Due: {inv.get('balance')}")

print("\n=== 5. UNPAID BILLS (PAYABLES) ===")
bill_res = requests.get(f'{ZOHO_BOOKS_API_URL}/bills?organization_id={org}&status=unpaid', headers=headers).json()
bills = bill_res.get('bills', [])
print(f"Total Unpaid Bills Count: {len(bills)}")
total_bill_bal = sum(float(b.get('balance', 0) or 0) for b in bills)
print(f"Total Unpaid Bills Balance: Rs. {total_bill_bal:,.2f}")
for bill in bills[:5]:
    print(f"  Bill#: {bill.get('bill_number')} | Vendor: {bill.get('vendor_name')} | Due: {bill.get('balance')}")
