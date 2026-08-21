"""
Test query parameters like ?v=2 or ?refresh=1 to see if LiteSpeed serves the new 240K HTML.
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

for param in ['v=2', 'refresh=1', 'nocache=1', 'version=2026']:
    url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?{param}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            has_toggle = 'confirmToggleSubReport' in html
            has_sub = 'sub_reports_status' in html
            print(f"URL: {url} -> Size: {len(html)} | Has Toggle: {has_toggle} | Has Sub: {has_sub}")
    except Exception as e:
        print(f"Error {url}: {e}")

