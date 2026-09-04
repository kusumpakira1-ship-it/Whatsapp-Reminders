import urllib.request
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?nocache=1&cb={time.time()}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'Expires': '0',
    'Hostinger-Bypass-CDN': '1',
    'X-Hostinger-CDN-Cache': 'bypass',
    'CDN-Cache-Control': 'no-store'
}

print("Testing CDN bypass request to:", url)
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"HTTP Body Length: {len(html)} bytes")
        has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
        has_mon_fri = 'value="mon-fri"' in html or 'Mon to Fri' in html
        print(f"Contains 'Mon to Sat': {has_mon_sat}")
        print(f"Contains 'Mon to Fri': {has_mon_fri}")
        if has_mon_sat and has_mon_fri:
            print("SUCCESS: Fresh code retrieved from live server!")
        else:
            print("Response length:", len(html))
except Exception as e:
    print("Fetch error:", e)
