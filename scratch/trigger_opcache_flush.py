"""
Trigger opcache flush and cache clear on Hostinger server for frontend/index.php.
"""
import urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/flush_opcache.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/clear_all_cache.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/purge_cache.php"
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"URL: {url} -> Status: {resp.status_code}")
    except Exception as e:
        print(f"URL: {url} -> Notice: {e}")

