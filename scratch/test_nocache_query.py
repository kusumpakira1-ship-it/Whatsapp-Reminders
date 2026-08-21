"""
Test fetching index.php with cache buster query parameters
"""

import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

ts = int(time.time())
urls = [
    f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?v={ts}',
    f'https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?v={ts}'
]

for u in urls:
    try:
        req = urllib.request.Request(u, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            has_func = 'confirmToggleSubReport' in content
            print(f"URL: {u}")
            print(f"• Has confirmToggleSubReport? {'YES ✅' if has_func else 'NO ❌'}")
    except Exception as e:
        print(f"URL {u} Error: {e}")
