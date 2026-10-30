import sys
import requests
import json
sys.stdout.reconfigure(encoding='utf-8')

token = '1000.8d220264e57b0769d33d563af8ad6e60.00c8c5adc99a673bed450fe928460800'
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

print("=== ORGANIZATIONS ===")
res = requests.get('https://www.zohoapis.com/books/v3/organizations', headers=headers).json()
for o in res.get('organizations', []):
    print(f"Org ID: {o.get('organization_id')} | Name: {o.get('name')} | Currency: {o.get('currency_code')}")

print("\n=== BANK & CASH ACCOUNTS FOR RAJ FARMS (904503869) ===")
res_banks = requests.get('https://www.zohoapis.com/books/v3/bankaccounts?organization_id=904503869', headers=headers).json()
for b in res_banks.get('bankaccounts', []):
    print(f"- Name: {b.get('account_name')} | Type: {b.get('account_type')} | Balance: {b.get('balance')}")

print("\n=== RECEIVABLES SUMMARY ===")
res_rec = requests.get('https://www.zohoapis.com/books/v3/reports/receivablessummary?organization_id=904503869', headers=headers).json()
print("Receivables total:", res_rec.get('receivables_summary', {}).get('total_receivable', 'N/A'))

print("\n=== PAYABLES SUMMARY ===")
res_pay = requests.get('https://www.zohoapis.com/books/v3/reports/payablessummary?organization_id=904503869', headers=headers).json()
print("Payables total:", res_pay.get('payables_summary', {}).get('total_payable', 'N/A'))
