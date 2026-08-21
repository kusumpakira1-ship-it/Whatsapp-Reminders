"""
Test if Hostinger CDN bypasses cache when ?api= is in query string!
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

for param in ['api=1', 'api=page', 'api=home', 'api=view', 'api=dashboard']:
    url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?{param}&t={int(time.time())}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            print(f"URL: {url} -> Status: {resp.status}, Size: {len(content)}")
            print(f"  Has 'confirmToggleSubReport': {'confirmToggleSubReport' in content}")
            print(f"  Has 'sub_reports_status': {'sub_reports_status' in content}\n")
    except Exception as e:
        print(f"Error {url}: {e}\n")

