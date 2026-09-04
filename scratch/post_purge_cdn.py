import urllib.request
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php"

print("=== 1. SENDING POST REQUEST TO PURGE EDGE CDN CACHE ===")
req_post = urllib.request.Request(url, data=b'purge=1', headers={
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-LiteSpeed-Purge': '*'
})
try:
    with urllib.request.urlopen(req_post, timeout=10) as resp:
        print(f"POST Response Code: {resp.status}")
except Exception as e:
    print(f"POST Error: {e}")

time.sleep(2)

print("\n=== 2. GETTING FRESH GET RESPONSE ===")
req_get = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Cache-Control': 'no-cache, no-store, must-revalidate'
})

try:
    with urllib.request.urlopen(req_get, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"GET Length: {len(html)} bytes")
        has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
        has_mon_fri = 'value="mon-fri"' in html or 'Mon to Fri' in html
        print(f"Contains 'Mon to Sat': {has_mon_sat}")
        print(f"Contains 'Mon to Fri': {has_mon_fri}")
except Exception as e:
    print(f"GET Error: {e}")
