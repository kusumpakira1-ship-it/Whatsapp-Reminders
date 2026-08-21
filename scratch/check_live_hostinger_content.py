"""
Fetch live Hostinger URL and check if confirmToggleSubReport exists in the output
"""

import urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/index.php'
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            has_func = 'confirmToggleSubReport' in content
            has_sub_status = 'sub_reports_status' in content
            print(f"URL: {url}")
            print(f"• Size: {len(content)} bytes")
            print(f"• Has confirmToggleSubReport? {'YES ✅' if has_func else 'NO ❌'}")
            print(f"• Has sub_reports_status? {'YES ✅' if has_sub_status else 'NO ❌'}\n")
    except Exception as e:
        print(f"URL {url} Error: {e}\n")
