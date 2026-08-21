"""
Test accessing marker_test.php, get_path.php, cdn_test.php via HTTP to see if they execute.
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

test_urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/marker_test.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/marker_test.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/get_path.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/get_path.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/cdn_test.php',
]

for url in test_urls:
    req = urllib.request.Request(f"{url}?t={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f"URL: {url} -> Status: {resp.status}, Size: {len(content)}")
            print(f"  Content snippet: {content[:200].strip()}\n")
    except Exception as e:
        print(f"Error {url}: {e}\n")

