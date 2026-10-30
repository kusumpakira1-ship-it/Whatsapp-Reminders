import sys
import os
import requests
import time
sys.stdout.reconfigure(encoding='utf-8')

token = '1000.8d220264e57b0769d33d563af8ad6e60.00c8c5adc99a673bed450fe928460800'
org_id = '904503869'
headers = {'Authorization': f'Zoho-oauthtoken {token}'}

t0 = time.time()
print(f"[{time.time()-t0:.1f}s] Testing Loans...", flush=True)
res_bs = requests.get(f'https://www.zohoapis.com/books/v3/reports/balancesheet?organization_id={org_id}', headers=headers, timeout=10).json()
print(f"[{time.time()-t0:.1f}s] BS response keys: {list(res_bs.keys())}", flush=True)

print(f"[{time.time()-t0:.1f}s] Testing Sales/Purchases...", flush=True)
res_inv = requests.get(f'https://www.zohoapis.com/books/v3/invoices?organization_id={org_id}&date=2026-10-29', headers=headers, timeout=10).json()
print(f"[{time.time()-t0:.1f}s] Invoices today: {len(res_inv.get('invoices', []))}", flush=True)

print(f"[{time.time()-t0:.1f}s] Done all tests!", flush=True)
