"""
Test ?api=tasks on index.php
"""
import urllib.request

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=tasks"
print(f"=== TESTING URL: {url} ===")
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read().decode('utf-8')
        print(f"HTTP Status: {resp.status}")
        print(f"Content Length: {len(content)}")
        print("Content Snippet (First 500 chars):")
        print(content[:500])
except Exception as e:
    print(f"Error fetching {url}: {e}")
