"""
Test index.php?v=2026 and check if OPcache recompile is active!
"""
import urllib.request, time, sys
sys.stdout.reconfigure(encoding='utf-8')

url = f"https://sunfragroup.com/kusum/Whatsapp_Rem/frontend/index.php?v=2026&ts={int(time.time())}"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')
    print("URL:", url)
    print("  Size:", len(html))
    print("  Has 'OPCACHE_FORCE_RECOMPILE':", 'OPCACHE_FORCE_RECOMPILE' in html)
    print("  Has 'remindersDatePicker':", 'remindersDatePicker' in html)
    print("  Has 'sub_reports_status':", 'sub_reports_status' in html)

