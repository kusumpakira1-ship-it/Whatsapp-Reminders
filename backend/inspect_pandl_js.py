import requests
import re

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_pandl = "https://sunfra.com/farm/sunfra/profit_and_loss_details/profit_loss_json_to_web.php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'})
resp = session.get(url_pandl)
html = resp.text

print("=== SEARCHING FOR AJAX / API ENDPOINTS IN P&L HTML ===")
# Find script tags
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
print(f"Total <script> blocks found: {len(scripts)}")

for idx, s in enumerate(scripts, 1):
    print(f"\n--- SCRIPT BLOCK #{idx} ---")
    urls = re.findall(r'["\']([^"\']+\.php[^"\']*)["\']', s, re.IGNORECASE)
    fetch_calls = re.findall(r'fetch\((.*?)\)', s, re.IGNORECASE)
    ajax_calls = re.findall(r'\$\.ajax\((.*?)\)', s, re.DOTALL | re.IGNORECASE)
    
    if urls:
        print("  PHP Endpoints referenced:", urls)
    if fetch_calls:
        print("  Fetch calls:", fetch_calls[:3])
    if ajax_calls:
        print("  Ajax calls snippet:", ajax_calls[0][:200])

# Also check for form elements
forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL | re.IGNORECASE)
print(f"\nTotal Forms found: {len(forms)}")
for idx, f in enumerate(forms, 1):
    print(f"Form #{idx}:", f[:500])

# Print full HTML script content if small
print("\n--- FULL SCRIPT CONTENTS ---")
for idx, s in enumerate(scripts, 1):
    if len(s.strip()) > 0:
        print(f"\nScript #{idx}:\n", s[:1500])
