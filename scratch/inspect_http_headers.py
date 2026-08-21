"""
Inspect HTTP headers of responses from sunfragroup.com to see CDN cache status.
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/dashboard.php?t={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("HTTP Status:", resp.status)
        print("\n--- Response Headers ---")
        for k, v in resp.headers.items():
            print(f"{k}: {v}")
except Exception as e:
    print("Error:", e)

