"""
Debug API response from Hostinger
"""
import urllib.request
import json

urls = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=reminders",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php?api=tasks"
]

for url in urls:
    print(f"=== TESTING URL: {url} ===")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8')
            print(f"HTTP Status: {resp.status}")
            print(f"Content Length: {len(content)}")
            try:
                data = json.loads(content)
                print(f"Parsed JSON element count: {len(data)}")
                if len(data) > 0:
                    print("Sample item 0:", data[0])
            except Exception as je:
                print("JSON Parse Error:", je)
                print("Raw output:", content[:400])
    except Exception as e:
        print("HTTP Error:", e)
    print("=" * 60)
