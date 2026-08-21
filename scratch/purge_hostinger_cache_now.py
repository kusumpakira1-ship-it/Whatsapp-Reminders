"""
Trigger cache purges on Hostinger web server
"""
import urllib.request

urls = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/purge_cache.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/do_reset.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/flush_opcache.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/clear_all_cache.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/purge_cache.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/do_reset.php"
]

for u in urls:
    print(f"Purging cache via {u}...")
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            print("Response:", resp.read().decode('utf-8')[:200])
    except Exception as e:
        print("Error:", e)
