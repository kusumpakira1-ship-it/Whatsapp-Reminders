"""
Send HTTP PURGE and BAN requests to Hostinger CDN edge to purge all cached URLs!
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/index.php',
]

methods = ['PURGE', 'BAN', 'FLUSH']

for url in urls:
    for method in methods:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'X-Purge-Key': '*', 'X-LiteSpeed-Purge': '*'}, method=method)
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"Sent {method} to {url} -> Status: {resp.status}")
        except Exception as e:
            print(f"{method} {url} -> {e}")

