"""
Test HTTP access to sunfra.com endpoints and check response cookies/login.
"""
import urllib.request, http.cookiejar, json, sys
sys.stdout.reconfigure(encoding='utf-8')

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'),
    ('Accept', 'application/json, text/javascript, */*; q=0.01'),
    ('X-Requested-With', 'XMLHttpRequest')
]

urls = [
    "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php",
    "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json_to_web.php",
    "https://sunfra.com/farm/sunfra/supervisor/supervisor_birds_weight_json_to_web.php"
]

for url in urls:
    try:
        resp = opener.open(url, timeout=10)
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"\nURL: {url}")
        print(f"  Status: {resp.status}, Size: {len(html)} bytes")
        print(f"  First 300 chars: {html[:300]}")
    except Exception as e:
        print(f"Error {url}: {e}")

