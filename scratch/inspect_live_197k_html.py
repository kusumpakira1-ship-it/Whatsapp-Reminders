"""
Inspect the 197K live HTML served by LiteSpeed cache.
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?t={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})

with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print("Live HTML size:", len(html))
    
    # Check if 'subStatus' or 'sub_reports_status' is in the JS in this 197K HTML
    print("Contains 'sub_reports_status':", 'sub_reports_status' in html)
    print("Contains 'confirmToggleSubReport':", 'confirmToggleSubReport' in html)
    print("Contains 'Viewing':", 'Viewing' in html)
    
    # Find where 'Viewing' appears in the 197K HTML
    idx = html.find('Viewing')
    if idx != -1:
        print("\nSnippet around 'Viewing':")
        print(html[max(0, idx-100):min(len(html), idx+300)])

