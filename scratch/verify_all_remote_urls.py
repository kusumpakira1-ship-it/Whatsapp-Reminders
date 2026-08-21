"""
Verify all remote PHP endpoints on sunfragroup.com to check HTML content and cache headers.
"""
import sys, time, requests
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    "https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php",
    "https://sunfragroup.com/kusum/Whatsapp_Rem/index.php",
    "https://sunfragroup.com/kusum/index.php",
    "https://sunfragroup.com/frontend/index.php",
    "https://sunfragroup.com/index.php"
]

print("--- VERIFYING ALL REMOTE PHP ENDPOINTS ---")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache'
}

for base_url in urls:
    cache_buster = f"?v={int(time.time())}"
    target_url = base_url + cache_buster
    try:
        r = requests.get(target_url, headers=headers, timeout=10)
        html = r.text
        has_undone = ("↩️ Undone" in html) or ("Undone" in html and "resetAllSubReports" in html)
        has_button_pill = ("confirmToggleSubReport" in html)
        has_try_onload = ("fetchWahaGroups notice" in html) or ("loadReportTypesDropdowns notice" in html)
        print(f"\nURL: {base_url}")
        print(f"  - Status Code: {r.status_code}")
        print(f"  - Has 'Undone' button code: {has_undone}")
        print(f"  - Has interactive button pills: {has_button_pill}")
        print(f"  - Has try-catch onload guards: {has_try_onload}")
        print(f"  - Content Length: {len(html)} bytes")
    except Exception as e:
        print(f"URL: {base_url} Error: {e}")
