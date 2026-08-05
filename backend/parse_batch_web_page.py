import requests
import re

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_batch_page = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
})

session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'})
resp = session.get(url_batch_page)
html = resp.text

print("=== FULL HTML OF BATCH PAGE (Snippet) ===")
print(html[:2500])

scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
print(f"\nTotal Scripts: {len(scripts)}")
for idx, s in enumerate(scripts, 1):
    print(f"\n--- SCRIPT #{idx} ---")
    print(s[:1500])
