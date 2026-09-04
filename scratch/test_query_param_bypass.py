import urllib.request
import sys

sys.stdout.reconfigure(encoding='utf-8')

params = [
    "",
    "?v=2026",
    "?nocache=true",
    "?purge=1",
    "?ref=live",
    "?x=12345",
    "?ver=999"
]

for p in params:
    url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/index.php{p}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache'
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            length = len(html)
            has_mon_sat = 'value="mon-sat"' in html or 'Mon to Sat' in html
            print(f"URL: {url} -> len={length}, Mon-Sat={has_mon_sat}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
