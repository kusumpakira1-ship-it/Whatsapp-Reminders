"""
Test different query params to bypass Hostinger CDN edge cache
"""
import sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

test_params = [
    "?nocache=true",
    "?purge=1",
    "?bypass=true",
    f"?cb={int(time.time())}",
    f"?v={int(time.time())}&nocache=1",
    "?api=temp_read_file"
]

base = "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'X-Hostinger-CDN-Cache': 'bypass',
    'CDN-Cache-Control': 'no-store'
}

for p in test_params:
    url = base + p
    try:
        r = requests.get(url, headers=headers, timeout=10)
        html = r.text
        has_undone = "resetAllSubReports" in html
        cdn_status = r.headers.get('x-hcdn-cache-status', 'NONE')
        print(f"URL: {p} => Length: {len(html)} | HasUndone: {has_undone} | CDN-Status: {cdn_status}")
    except Exception as e:
        print(f"Error {p}: {e}")
