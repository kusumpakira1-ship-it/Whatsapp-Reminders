"""
Test ?api=app live HTML output!
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?api=app&t={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"URL: {url} -> Status: {resp.status}, Size: {len(html)} bytes")
        print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
        print(f"  Has 'changeRemindersViewingDate': {'changeRemindersViewingDate' in html}")
        print(f"  Has 'confirmToggleSubReport': {'confirmToggleSubReport' in html}")
except Exception as e:
    print(f"Error: {e}")

