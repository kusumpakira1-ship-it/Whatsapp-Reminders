import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php"

headers_variants = [
    {'User-Agent': 'Mozilla/5.0', 'X-Hostinger-CDN-Cache': 'bypass'},
    {'User-Agent': 'Mozilla/5.0', 'CDN-Cache-Control': 'no-store'},
    {'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0'},
    {'User-Agent': 'Mozilla/5.0', 'X-LiteSpeed-Purge': '*'},
    {'User-Agent': 'Mozilla/5.0', 'X-Purge': 'true'}
]

for i, h in enumerate(headers_variants):
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            length = len(html)
            has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
            print(f"Header Variant {i+1}: Length={length}, Mon-Sat={has_mon_sat}")
    except Exception as e:
        print(f"Header Variant {i+1} Error: {e}")
