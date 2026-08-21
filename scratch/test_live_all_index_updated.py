"""
Test live site after updating all index.php files!
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php',
    'https://sunfragroup.com/kusum/Whatsapp_Rem/index.php',
    'https://sunfragroup.com/index.php',
]

for url in urls:
    full_url = f"{url}?t={int(time.time())}"
    try:
        req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f"URL: {full_url}")
            print(f"  Size: {len(html)} bytes")
            print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
            print(f"  Has 'changeRemindersViewingDate': {'changeRemindersViewingDate' in html}")
            print(f"  Has 'sub_reports_status': {'sub_reports_status' in html}\n")
    except Exception as e:
        print(f"Error {full_url}: {e}\n")

