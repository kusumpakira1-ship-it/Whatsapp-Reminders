"""
The 197149-byte version is being served REGARDLESS of what we upload.
This is clearly a CDN/edge caching issue where Hostinger's hcdn is caching the response body.
The x-hcdn-cache-status=DYNAMIC means each PHP execution SHOULD be fresh,
but the content is still 197K.

Let me check if the RESPONSE is actually coming from a CDN cached object by
looking at the x-hcdn-request-id header (it should change on each request if truly dynamic).
Also let me try using a POST request to bypass CDN cache.
"""
import urllib.request, sys, time
sys.stdout.reconfigure(encoding='utf-8')

# Check if x-hcdn-request-id changes on each request (proves it's not CDN cached)
print("Checking x-hcdn-request-id across 3 requests:")
for i in range(3):
    url = f'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?req={i}&t={int(time.time())}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        headers = dict(resp.headers)
        req_id = headers.get('x-hcdn-request-id', 'N/A')
        cache_status = headers.get('x-hcdn-cache-status', 'N/A')
        print(f"  Request {i+1}: size={len(html)}, cache={cache_status}, req_id={req_id}")
    time.sleep(0.5)

print()
# Try a POST request (CDN should NOT cache POST)
print("Trying POST request:")
req = urllib.request.Request(
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    data=b'test=1',
    headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    headers = dict(resp.headers)
    print(f"  POST: size={len(html)}, toggle={'YES' if 'confirmToggleSubReport' in html else 'NO'}")
    print(f"  cache-status: {headers.get('x-hcdn-cache-status', 'N/A')}")
