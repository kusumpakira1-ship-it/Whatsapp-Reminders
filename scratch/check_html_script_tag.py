"""
Inspect the HTML script tag of live Hostinger page
"""

import urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

print(f"Total HTML length: {len(html)} bytes")
print("Has 'confirmToggleSubReport'? ", 'confirmToggleSubReport' in html)
print("Has 'reportsText'? ", 'reportsText' in html)
print("Has 'sub_reports_status'? ", 'sub_reports_status' in html)

# Find where fetchReminders is in HTML
pos = html.find('function fetchReminders')
if pos != -1:
    print("\n--- Snippet around fetchReminders in live HTML ---")
    print(html[pos:pos+1200])
else:
    print("function fetchReminders not found!")
