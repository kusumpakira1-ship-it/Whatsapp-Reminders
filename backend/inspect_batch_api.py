import requests
import re

url_login = "https://sunfra.com/farm/sunfra/login/login.php"
url_batch_page = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
})

# Login
session.post(url_login, data={'username': 'sunfra', 'password': 'Sunfra#321', 'remember_me': '1'})
resp_batch = session.get(url_batch_page)
html = resp_batch.text

print("=== INSPECTING BATCH SECTION HTML & JS ===")
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
for idx, s in enumerate(scripts, 1):
    php_urls = re.findall(r'["\']([^"\']+\.php[^"\']*)["\']', s, re.IGNORECASE)
    if php_urls:
        print(f"Script #{idx} PHP URLs:", php_urls)

# Try fetching batch JSON API endpoints
for api_path in [
    "https://sunfra.com/farm/sunfra/batch/batch_json.php",
    "https://sunfra.com/farm/sunfra/batch/batch_master_json.php",
    "https://sunfra.com/farm/sunfra/batch/get_batch.php",
    "https://sunfra.com/farm/sunfra/batch/batch_list_json.php"
]:
    res = session.get(api_path)
    print(f"\nAPI URL [{api_path}] -> Code: {res.status_code}")
    if res.status_code == 200:
        print("Snippet:", res.text[:500])
        try:
            j = res.json()
            print("JSON Keys:", list(j.keys()) if isinstance(j, dict) else f"List len: {len(j)}")
            if isinstance(j, dict) and 'data' in j:
                for b in j['data'][:10]:
                    print("  • Batch:", b)
            elif isinstance(j, list):
                for b in j[:10]:
                    print("  • Batch:", b)
        except Exception as e:
            pass
