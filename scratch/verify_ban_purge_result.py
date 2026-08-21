"""
Test live site output after sending BAN purge request to Hostinger CDN edge!
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?t={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Cache-Control': 'no-cache'})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"URL: {url}")
        print(f"  Live HTML Size: {len(html)} bytes")
        print(f"  Has 'remindersDatePicker': {'remindersDatePicker' in html}")
        print(f"  Has 'changeRemindersViewingDate': {'changeRemindersViewingDate' in html}")
        print(f"  Has 'sub_reports_status': {'sub_reports_status' in html}")
except Exception as e:
    print("Error:", e)

