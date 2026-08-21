"""
Post login credentials to https://sunfra.com/farm/sunfra/ and fetch batch_json_to_web.php JSON!
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

# Post login credentials to base URL
login_url = "https://sunfra.com/farm/sunfra/"
post_data = urllib.parse.urlencode({
    'username': 'kusum',
    'password': 'Kusum@2026Bb!',
    'remember_me': '1'
}).encode('utf-8')

try:
    req = urllib.request.Request(login_url, data=post_data, headers=headers)
    resp = opener.open(req, timeout=10)
    print("Login POST status:", resp.status)
    print("Cookies set:", [c.name for c in cj])
except Exception as e:
    print("Login error:", e)

# Now fetch batch_json_to_web.php
batch_url = "https://sunfra.com/farm/sunfra/batch/batch_json_to_web.php"
try:
    req2 = urllib.request.Request(batch_url, headers={'User-Agent': headers['User-Agent']})
    with opener.open(req2, timeout=10) as resp2:
        raw = resp2.read().decode('utf-8', errors='ignore')
        print(f"\nResponse from {batch_url}:")
        print(f"Length: {len(raw)} bytes")
        try:
            data = json.loads(raw)
            print("JSON Output:")
            print(json.dumps(data, indent=2))
            with open(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\scratch\batch_json_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as je:
            print("Raw output (first 500 chars):", raw[:500])
except Exception as e:
    print("Batch fetch error:", e)

