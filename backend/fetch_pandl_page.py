import requests
import re

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_pandl = "https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json_to_web.php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
})

# Login
post_data = {'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'}
resp_login = session.post(url_login, data=post_data)
print("Login Status:", resp_login.status_code)

# Fetch P&L Page
resp_pandl = session.get(url_pandl)
print(f"P&L Page Status Code: {resp_pandl.status_code}")
print(f"P&L Page URL: {resp_pandl.url}")
html = resp_pandl.text

print("\n--- P&L PAGE TITLE & HEADERS ---")
title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
print("Title:", title.group(1) if title else "No Title")

# Extract HTML tables
tables = re.findall(r'<table[^>]*>(.*?)</table>', html, re.IGNORECASE | re.DOTALL)
print(f"\nTotal Tables Found on P&L Page: {len(tables)}")

for idx, tbl in enumerate(tables, 1):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl, re.IGNORECASE | re.DOTALL)
    print(f"\n--- TABLE #{idx} (Total Rows: {len(rows)}) ---")
    
    clean_rows = []
    for r_idx, r in enumerate(rows, 1):
        # Extract th and td cells
        cells = re.findall(r'<(?:td|th)[^>]*>(.*?)</(?:td|th)>', r, re.IGNORECASE | re.DOTALL)
        clean_cells = []
        for c in cells:
            # Strip tags and excess whitespace
            c_text = re.sub(r'<[^>]+>', ' ', c).strip()
            c_text = re.sub(r'\s+', ' ', c_text)
            clean_cells.append(c_text)
            
        # Check if row is non-empty
        non_empty = [c for c in clean_cells if c and c != '-' and c != '0' and c != '0.00']
        if clean_cells:
            status = "DATA" if non_empty else "EMPTY"
            print(f"Row {r_idx} [{status}]:", " | ".join(clean_cells))

if not tables:
    print("\nNo HTML <table> tags found. Printing HTML snippet:")
    print(html[:2000])
