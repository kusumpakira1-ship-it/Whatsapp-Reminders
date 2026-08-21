"""
Test fetching index.php with cache buster query parameter.
"""
import urllib.request, sys, time
sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?nocache={int(time.time())}"
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
})

with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print("Fetched HTML Total Length:", len(html))
    print("Contains 'confirmToggleSubReport':", "confirmToggleSubReport" in html)
    print("Contains 'resetAllSubReports':", "resetAllSubReports" in html)
    print("Contains 'Undone':", "Undone" in html)

