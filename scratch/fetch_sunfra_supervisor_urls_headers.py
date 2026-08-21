"""
Fetch JSON data from all 3 Sunfra supervisor URLs with full browser headers.
"""
import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

urls = {
    "mortality": "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php",
    "production": "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json_to_web.php",
    "birds_weight": "https://sunfra.com/farm/sunfra/supervisor/supervisor_birds_weight_json_to_web.php"
}

date_params = [
    "",
    "?date=2026-08-13",
    "?date=13-08-2026",
    "?entry_date=2026-08-13",
    "?select_date=2026-08-13"
]

for name, base_url in urls.items():
    print(f"\n==================== {name.upper()} ====================")
    for p in date_params:
        url = base_url + p
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode('utf-8', errors='ignore')
                print(f"\nURL: {url}")
                print(f"Response length: {len(raw)} bytes")
                try:
                    data = json.loads(raw)
                    print("JSON Output snippet:")
                    print(json.dumps(data, indent=2)[:1200])
                except Exception as je:
                    print(f"Raw Snippet (not JSON): {raw[:400]}")
        except Exception as e:
            print(f"Error {url}: {e}")

