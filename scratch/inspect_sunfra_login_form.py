"""
Inspect login form on https://sunfra.com/farm/sunfra/ with full browser headers.
"""
import urllib.request, re, sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}
req = urllib.request.Request('https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php', headers=headers)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        forms = re.findall(r'<form.*?>.*?</form>', html, re.DOTALL | re.IGNORECASE)
        print(f"Found {len(forms)} form(s):")
        for f in forms:
            print(f)
            print("-" * 50)
except Exception as e:
    print("Error:", e)

