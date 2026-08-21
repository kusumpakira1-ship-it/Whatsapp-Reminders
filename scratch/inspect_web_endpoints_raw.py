"""
Inspect raw JSON output from sunfra.com with full browser headers.
"""
import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

endpoints = {
    "Mortality (Today)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php?date=2026-08-15",
    "Mortality (Yesterday)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php?date=2026-08-14",
    "Production (Today)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json_to_web.php?date=2026-08-15",
    "Production (Yesterday)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json_to_web.php?date=2026-08-14",
    "Birds Weight (Today)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_birds_weight_json_to_web.php?date=2026-08-15",
    "Birds Weight (Yesterday)": "https://sunfra.com/farm/sunfra/supervisor/supervisor_birds_weight_json_to_web.php?date=2026-08-14",
    "Batch / Live Birds": "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"
}

for title, url in endpoints.items():
    print(f"\n==========================================================================")
    print(f" 🌐 {title}")
    print(f" URL: {url}")
    print(f"==========================================================================")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8').strip()
            print(f"Raw Output (first 500 chars):\n{content[:500]}\n")
            try:
                data = json.loads(content)
                print(f"Parsed JSON Type: {type(data)}")
                if isinstance(data, list):
                    print(f"Array length: {len(data)}")
                    for item in data:
                        print("  Item:", item)
                elif isinstance(data, dict):
                    print("Keys:", list(data.keys()))
                    for k, v in list(data.items()):
                        print(f"  {k}: {v}")
            except Exception as je:
                print(f"❌ JSON Parse Error: {je}")
    except Exception as e:
        print(f"❌ HTTP Fetch Error: {e}")

