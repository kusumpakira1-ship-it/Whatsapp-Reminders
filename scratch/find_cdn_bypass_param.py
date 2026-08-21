"""
Test 20 different query parameters to find which query string Hostinger CDN bypasses!
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

params = [
    'v=100', 'ver=2026', 'ts=99999', 'nocache=true', 'refresh=true',
    'view=1', 'page=1', 'mode=live', 'action=list', 'do=show',
    'date=2026-08-13', 'date=2026-08-14', 'r=123', 'q=test', 'app=1'
]

for p in params:
    url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?{p}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            size = len(html)
            has_dp = 'remindersDatePicker' in html
            has_sub = 'sub_reports_status' in html
            if has_dp or has_sub or size != 197149:
                print(f"🎉 SUCCESS! URL: {url} -> Size: {size} | Has DatePicker: {has_dp} | Has SubStatus: {has_sub}")
            else:
                print(f"Cached: {url} -> Size: {size}")
    except Exception as e:
        print(f"Error {url}: {e}")

