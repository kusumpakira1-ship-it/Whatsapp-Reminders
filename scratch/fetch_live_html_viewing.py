"""
Fetch live HTML from sunfragroup.com and search for 'Viewing' or 'Back to Today' or date picker element!
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/index.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/',
]

for url in urls:
    req = urllib.request.Request(f"{url}?t={int(time.time())}", headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"URL: {url} -> Length: {len(html)}")
            if 'viewing' in html.lower():
                print("  FOUND 'viewing' in HTML!")
            if 'back to today' in html.lower():
                print("  FOUND 'Back to Today' in HTML!")
            if 'sub_reports_status' in html:
                print("  FOUND 'sub_reports_status' in HTML!")
    except Exception as e:
        print(f"Error {url}: {e}")

