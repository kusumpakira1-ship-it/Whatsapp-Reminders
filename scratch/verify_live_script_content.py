"""
Verify raw HTML/JS content of https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php
"""
import urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

url = "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print("Fetched HTML Total Length:", len(html))
    print("Contains 'confirmToggleSubReport':", "confirmToggleSubReport" in html)
    print("Contains 'resetAllSubReports':", "resetAllSubReports" in html)
    print("Contains 'Undone':", "Undone" in html)

